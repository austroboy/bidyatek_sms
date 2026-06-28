from django.db import models
from django.utils import timezone
from core.models import Admission_Year


class BiometricDevice(models.Model):
    """
    Ekta school e ek ba ekadhik ZKTeco machine thakte pare.
    Protita machine er IP/port ekhane store kora hobe.
    NOTE: Eta TENANT_APPS er moddhe thakbe, tai protita school er
    nijossho device list thakbe (schema isolated).
    """

    class DeviceType(models.TextChoices):
        ZKTECO = 'ZKTECO', 'ZKTeco'

    name = models.CharField(max_length=100, help_text="e.g. Main Gate K40-H")
    device_type = models.CharField(
        max_length=20, choices=DeviceType.choices, default=DeviceType.ZKTECO
    )
    ip_address = models.CharField(max_length=50, help_text="e.g. 192.168.1.201")
    port = models.IntegerField(default=4370)
    password = models.IntegerField(
        default=0, help_text="Comm key. Device e set na thakle 0 din."
    )
    force_udp = models.BooleanField(
        default=False, help_text="Connect na hole eta True kore dekhun."
    )
    timeout = models.IntegerField(default=10)

    # K40-H ekta single device, kintu boro school e gate-in / gate-out
    # alada device hote pare. Eta diye thik kora hobe punch ta IN na OUT.
    is_exit_device = models.BooleanField(
        default=False,
        help_text="Eta jodi ber howar gate er machine hoy tahole tick din.",
    )

    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class DevicePunchLog(models.Model):
    """
    Device theke asha PROTITA raw punch ekhane raw obostha te store hobe.
    Eta audit / debug / duplicate check er jonno. Attendance table er
    sathe eta alada — eta hocche kacha (raw) data.
    """

    class Source(models.TextChoices):
        FINGERPRINT = 'FINGER', 'Fingerprint'
        CARD = 'CARD', 'RFID Card'
        PASSWORD = 'PASSWORD', 'Password'
        FACE = 'FACE', 'Face'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    class PersonType(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        STAFF = 'STAFF', 'Staff'
        UNMATCHED = 'UNMATCHED', 'Unmatched'

    device = models.ForeignKey(
        BiometricDevice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='punch_logs'
    )
    # Device e protita person er ekta numeric "user_id" thake.
    # Amra eta CustomUser.user_id er sathe map korbo.
    device_user_id = models.CharField(max_length=50)
    punch_time = models.DateTimeField()
    source = models.CharField(
        max_length=10, choices=Source.choices, default=Source.UNKNOWN
    )
    # Device theke asha raw status code (0=checkin,1=checkout etc)
    raw_status = models.IntegerField(null=True, blank=True)

    person_type = models.CharField(
        max_length=10, choices=PersonType.choices, default=PersonType.UNMATCHED
    )
    matched_user_id = models.BigIntegerField(
        null=True, blank=True,
        help_text="CustomUser.id jodi match hoy"
    )
    processed = models.BooleanField(
        default=False, help_text="Attendance + SMS process hoyeche kina"
    )
    sms_sent = models.BooleanField(default=False)
    note = models.CharField(max_length=255, null=True, blank=True)

    academic_year = models.ForeignKey(
        Admission_Year, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ekই device_user_id + ekই somoy duibar jeno na dhoke
        unique_together = ('device', 'device_user_id', 'punch_time')
        ordering = ['-punch_time']

    def __str__(self):
        return f"{self.device_user_id} @ {self.punch_time}"
