"""
device/management/commands/push_users_to_device.py
--------------------------------------------------
Database er student + staff der device e push kore (user_id, nam, RFID card)
jate device er bhitore tara registered hoy. Push howar por machine er
keypad/enroll mode theke protita user er finger choano jabe.

    python manage.py push_users_to_device --schema=<school_schema> --device-id=<id>

Optional:
    --students-only   sudhu student push korbe
    --staff-only      sudhu staff push korbe

KIBHABE kaj kore:
  - device er bhitore protita user er ekta "uid" (1,2,3..) lage — eta amra
    sequentially generate kori.
  - "user_id" hisebe amra CustomUser.user_id boshai (eta diye punch er somoy
    match korbo).
  - CustomUser.rfid (jodi numeric hoy) ke card number hisebe push kori.

Push korar PORE: machine er Menu > User Management > oi user select kore
finger enroll korben. Finger device er memory te oi user_id er sathe save
hobe. Erpor finger choalei punch hobe + amader listener SMS pathabe.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

logger = logging.getLogger('attendance')


class Command(BaseCommand):
    help = "DB er student/staff der device e push kore (enroll er age)."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True)
        parser.add_argument('--device-id', type=int, required=True)
        parser.add_argument('--students-only', action='store_true')
        parser.add_argument('--staff-only', action='store_true')

    def handle(self, *args, **options):
        schema = options['schema']
        device_id = options['device_id']

        from device.models import BiometricDevice
        from device.zk_client import ZKClient
        from user.models import StudentProfile, StaffProfile

        with schema_context(schema):
            device = BiometricDevice.objects.filter(id=device_id).first()
            if not device:
                raise CommandError(f"Device {device_id} pawa gelo na.")

            users_to_push = []  # (user_id, name, card)

            if not options['staff_only']:
                students = StudentProfile.objects.filter(
                    student_field__status="Active"
                ).select_related('student_field')
                for sp in students:
                    cu = sp.student_field
                    if cu.user_id:
                        card = self._card_int(cu.rfid)
                        users_to_push.append((cu.user_id, cu.name or "Student", card))

            if not options['students_only']:
                staffs = StaffProfile.objects.select_related('staff_field').all()
                for stp in staffs:
                    cu = stp.staff_field
                    if cu.user_id:
                        card = self._card_int(cu.rfid)
                        users_to_push.append((cu.user_id, cu.name or "Staff", card))

        if not users_to_push:
            self.stdout.write(self.style.WARNING("Push korar moto user nai (user_id set ache to?)."))
            return

        client = ZKClient(device)
        try:
            conn = client.connect()
            conn.disable_device()

            uid = 1
            pushed = 0
            for user_id, name, card in users_to_push:
                try:
                    client.set_user(
                        uid=uid, user_id=user_id, name=name, card=card,
                    )
                    pushed += 1
                except Exception as e:  # noqa
                    self.stderr.write(self.style.ERROR(
                        f"user_id={user_id} push fail: {e}"
                    ))
                uid += 1

            conn.enable_device()
            self.stdout.write(self.style.SUCCESS(
                f"{pushed} ta user device e push holo. "
                f"Ekhon machine er User menu theke finger enroll korun."
            ))
        finally:
            client.disconnect()

    @staticmethod
    def _card_int(rfid):
        """rfid numeric hole int e convert kore, na hole 0."""
        if not rfid:
            return 0
        try:
            return int(str(rfid).strip())
        except ValueError:
            return 0
