"""
device/services.py
-------------------
Ekhane attendance + SMS er core business logic ache.

Workflow (ekta punch asar por):
1. device_user_id -> CustomUser khuje ber kora (user_id ba rfid diye)
2. Student naki Staff seta ber kora
3. Ajker attendance status=True (present) kore save kora
4. Sathe sathe SMS pathano (student hole parent, staff hole nije)
5. Sob kichu DevicePunchLog e track kora

NOTE: Project ta MULTI-TENANT (django_tenants). Tai ei function gulo
SHOBSOMOY ekta tenant schema context er bhitore call hote hobe.
(management command / live capture e amra schema_context diye call korbo)
"""

from datetime import date, datetime
import logging

from django.utils import timezone
from django.db import transaction

from core.models import Admission_Year
from shared.models import CustomUser
from user.models import StudentProfile, StaffProfile
from attendance.models import (
    StudentAttendance, StudentAttendanceLog,
    StaffAttendance, StaffAttendanceLog,
    Holiday,
)
from crucial.models import SMSUsage, SMSTemplateNotification, SMS
from sms.utils import send_sms, count_sms

from .models import DevicePunchLog

logger = logging.getLogger('attendance')


# ---------------------------------------------------------------------------
# Helper: phone number format (existing project er moto: 880 + number)
# ---------------------------------------------------------------------------
def _format_number(raw_number):
    if not raw_number:
        return None
    return '880' + str(raw_number).lstrip('0')


# ---------------------------------------------------------------------------
# Helper: ekta numeric SMS limit thik ache kina + decrement kore pathay
# (project er existing pattern hubohu follow kora hoyeche)
# ---------------------------------------------------------------------------
def _dispatch_sms(formatted_number, raw_number, sms_body, title, created_by=None):
    if not formatted_number:
        return False, "No phone number"

    sms_count = count_sms(sms_body)
    sms_limit_obj = SMSUsage.objects.filter(Msg_type='NONMASKING').first()

    if not sms_limit_obj or sms_limit_obj.total_sms < sms_count:
        logger.warning("SMS LIMIT OVER - cannot send to %s", formatted_number)
        return False, "SMS limit over"

    try:
        send_sms(formatted_number, sms_body)
        sms_limit_obj.total_sms -= sms_count
        sms_limit_obj.save()
        SMS.objects.create(
            mobile=raw_number, title=title, msg=sms_body, created_by=created_by
        )
        return True, "sent"
    except Exception as e:  # noqa
        logger.exception("SMS send failed: %s", e)
        return False, str(e)


# ---------------------------------------------------------------------------
# Helper: device_user_id theke CustomUser khuje ber kora.
# Amra duita strategy use korbo:
#   (1) CustomUser.user_id (BigInteger, unique) er sathe match
#   (2) na pele CustomUser.rfid er sathe match
# Device e enroll korar somoy user_id = CustomUser.user_id rakhle (1) kaj korbe.
# ---------------------------------------------------------------------------
def resolve_user(device_user_id):
    user = None
    # strategy 1: numeric user_id
    try:
        uid = int(str(device_user_id).strip())
        user = CustomUser.objects.filter(user_id=uid).first()
    except (ValueError, TypeError):
        user = None

    # strategy 2: rfid string match (card enroll holе)
    if user is None:
        user = CustomUser.objects.filter(rfid=str(device_user_id).strip()).first()

    return user


def _get_admission_year():
    current_year = str(datetime.now().year)
    return Admission_Year.objects.filter(name=current_year).first()


def _is_holiday_or_weekend(target_date, admission_year):
    if target_date.weekday() == 5:  # Saturday weekend (project er existing logic)
        return True
    if Holiday.objects.filter(
        holiday_date=target_date, academic_year=admission_year
    ).exists():
        return True
    return False


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================
@transaction.atomic
def process_punch(device_user_id, punch_time=None, device=None,
                  source='UNKNOWN', raw_status=None):
    """
    Ekta punch process kore. Returns DevicePunchLog instance.

    device_user_id : device theke asha id (string)
    punch_time     : datetime (na dile akhonkar somoy)
    device         : BiometricDevice instance (optional)
    source         : 'FINGER' / 'CARD' / etc
    raw_status     : device er status code
    """
    if punch_time is None:
        punch_time = timezone.now()

    admission_year = _get_admission_year()

    # duplicate guard: ekই device+user+time age dhukle abar na
    existing = DevicePunchLog.objects.filter(
        device=device,
        device_user_id=str(device_user_id),
        punch_time=punch_time,
    ).first()
    if existing:
        return existing

    log = DevicePunchLog.objects.create(
        device=device,
        device_user_id=str(device_user_id),
        punch_time=punch_time,
        source=source if source in dict(DevicePunchLog.Source.choices) else 'UNKNOWN',
        raw_status=raw_status,
        academic_year=admission_year,
    )

    user = resolve_user(device_user_id)
    if user is None:
        log.person_type = DevicePunchLog.PersonType.UNMATCHED
        log.note = "Device user_id/rfid kono CustomUser er sathe match holo na."
        log.processed = True
        log.save()
        logger.info("Unmatched punch: %s", device_user_id)
        return log

    log.matched_user_id = user.id

    # Student naki Staff? Profile diye ber kori.
    # student_field -> Student (proxy of CustomUser), staff_field -> CustomUser.
    # Proxy hole o pk same, tai _id diye match kora nirapod.
    student_profile = StudentProfile.objects.filter(
        student_field_id=user.id, student_field__status="Active"
    ).first()
    staff_profile = StaffProfile.objects.filter(staff_field_id=user.id).first()

    if student_profile:
        _handle_student(log, student_profile, punch_time, admission_year)
    elif staff_profile:
        _handle_staff(log, staff_profile, punch_time, admission_year)
    else:
        log.person_type = DevicePunchLog.PersonType.UNMATCHED
        log.note = "User mile6e kintu Student/Staff profile nai."
        log.processed = True
        log.save()
        return log

    return log


# ---------------------------------------------------------------------------
# STUDENT punch handle
# ---------------------------------------------------------------------------
def _handle_student(log, student_profile, punch_time, admission_year):
    today = punch_time.date()
    is_exit = bool(log.device and log.device.is_exit_device)

    # exit device hole status=False (ber holo), na hole True (dhuklo)
    status_value = False if is_exit else True

    obj, created = StudentAttendance.objects.update_or_create(
        name=student_profile,
        attendance_date=today,
        defaults={'status': status_value, 'academic_year': admission_year},
    )
    # log entry (ke kokhon in/out korlo)
    StudentAttendanceLog.objects.create(
        student_attendance=obj, status=status_value, changed_by=None
    )

    log.person_type = DevicePunchLog.PersonType.STUDENT
    log.processed = True

    # ---------- SMS ----------
    name = student_profile.student_field.name
    parent = student_profile.parent_id
    raw_number = parent.phone_number if parent else None
    formatted = _format_number(raw_number)

    notif_type = 'Attendance Absent' if is_exit else 'Attendance Present'
    template = SMSTemplateNotification.objects.filter(
        notification_type=notif_type, notification_status='Active'
    ).first()

    in_time = punch_time.strftime('%I:%M %p')
    today_date = today.strftime('%B %d, %Y')
    day_name = today.strftime('%A')

    if template:
        # template er placeholder gulo project er existing pattern follow kore
        try:
            sms_body = template.body.format(
                name=name, today_date=today_date,
                day_name=day_name, in_time=in_time,
            )
        except (KeyError, IndexError):
            sms_body = template.body
    else:
        # template na thakle default Bangla message
        if is_exit:
            sms_body = "{} স্কুল থেকে বের হয়েছে। সময়: {}।".format(name, in_time)
        else:
            sms_body = "{} স্কুলে উপস্থিত হয়েছে। সময়: {}।".format(name, in_time)

    sent, _msg = _dispatch_sms(
        formatted, raw_number, sms_body, title='Attendance Info'
    )
    log.sms_sent = sent
    log.save()
    return log


# ---------------------------------------------------------------------------
# STAFF punch handle
# ---------------------------------------------------------------------------
def _handle_staff(log, staff_profile, punch_time, admission_year):
    today = punch_time.date()
    is_exit = bool(log.device and log.device.is_exit_device)
    status_value = False if is_exit else True

    obj, created = StaffAttendance.objects.update_or_create(
        name=staff_profile,
        attendance_date=today,
        defaults={'status': status_value, 'academic_year': admission_year},
    )
    StaffAttendanceLog.objects.create(
        staff_attendance=obj, status=status_value, changed_by=None
    )

    log.person_type = DevicePunchLog.PersonType.STAFF
    log.processed = True

    # ---------- SMS (staff er nijer number e) ----------
    name = staff_profile.staff_field.name
    raw_number = staff_profile.staff_field.phone_number
    formatted = _format_number(raw_number)

    in_time = punch_time.strftime('%I:%M %p')
    if is_exit:
        sms_body = "{}, আপনি অফিস ত্যাগ করেছেন। সময়: {}।".format(name, in_time)
    else:
        sms_body = "{}, আপনি উপস্থিত হয়েছেন। সময়: {}।".format(name, in_time)

    sent, _msg = _dispatch_sms(
        formatted, raw_number, sms_body, title='Staff Attendance'
    )
    log.sms_sent = sent
    log.save()
    return log
