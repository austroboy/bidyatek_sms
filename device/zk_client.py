"""
device/zk_client.py
-------------------
pyzk diye ZKTeco machine er sathe communication.

Install lagbe:
    pip install pyzk

K40-H ekta TFT series device (firmware ~6.60), tai pyzk perfectly support kore.
Eta diye amra:
  - device theke registered user list ana
  - notun user (RFID/name) push kora
  - fingerprint template up/download
  - REALTIME live capture (punch holei event)
  - batch e attendance record download
kortে parbo.
"""

import logging

logger = logging.getLogger('attendance')

try:
    from zk import ZK, const
except ImportError:  # pyzk install na thakle bujhar jonno
    ZK = None
    const = None


class ZKClient:
    """BiometricDevice instance theke connection banay."""

    def __init__(self, device):
        if ZK is None:
            raise ImportError(
                "pyzk install kora nai. Run: pip install pyzk"
            )
        self.device = device
        self.zk = ZK(
            device.ip_address,
            port=device.port,
            timeout=device.timeout,
            password=device.password or 0,
            force_udp=device.force_udp,
            ommit_ping=False,
        )
        self.conn = None

    # ------------------------------------------------------------------
    def connect(self):
        self.conn = self.zk.connect()
        return self.conn

    def disconnect(self):
        if self.conn:
            try:
                self.conn.disconnect()
            except Exception:  # noqa
                pass
            self.conn = None

    # ------------------------------------------------------------------
    # USERS
    # ------------------------------------------------------------------
    def get_users(self):
        """Device e enrolled shob user (list of User object)."""
        return self.conn.get_users()

    def set_user(self, uid, user_id, name, card=0, privilege=0, password=''):
        """
        Device e ekta user add/update kore.
          uid     : device er internal index (1,2,3...) — unique hote hobe
          user_id : amra ekhane CustomUser.user_id boshabo (string)
          name    : student/staff er nam
          card    : RFID card number (integer). 0 hole card nai.
        Eta call korar por device er keypad theke ba enroll software theke
        finger ta oi user_id er sathe enroll kora jabe.
        """
        self.conn.set_user(
            uid=uid,
            name=str(name)[:24],
            privilege=privilege or (const.USER_DEFAULT if const else 0),
            password=str(password),
            user_id=str(user_id),
            card=int(card) if card else 0,
        )

    def delete_user(self, uid=0, user_id=''):
        self.conn.delete_user(uid=uid, user_id=str(user_id))

    # ------------------------------------------------------------------
    # FINGERPRINT TEMPLATES
    # ------------------------------------------------------------------
    def get_templates(self):
        return self.conn.get_templates()

    def get_user_template(self, uid, temp_id=0):
        return self.conn.get_user_template(uid=uid, temp_id=temp_id)

    def save_user_template(self, user, fingers):
        """user = User object, fingers = list of Finger object (max 10)."""
        self.conn.save_user_template(user, fingers)

    # ------------------------------------------------------------------
    # ATTENDANCE (batch / offline records)
    # ------------------------------------------------------------------
    def get_attendance(self):
        """Device er memory te joma thaka shob punch record."""
        return self.conn.get_attendance()

    def clear_attendance(self):
        self.conn.clear_attendance()

    # ------------------------------------------------------------------
    # REALTIME LIVE CAPTURE  ← instant SMS er asol jinish
    # ------------------------------------------------------------------
    def live_capture(self):
        """
        Generator: jokhonই keu finger/card punch korbe, sathe sathe
        ekta Attendance object yield korbe (ba None timeout e).
        Eta block kore — tai ekta alada process/management command e cholbe.
        """
        for attendance in self.conn.live_capture():
            yield attendance

    # ------------------------------------------------------------------
    def enable_device(self):
        self.conn.enable_device()

    def disable_device(self):
        self.conn.disable_device()
