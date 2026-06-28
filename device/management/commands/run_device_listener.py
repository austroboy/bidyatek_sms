"""
device/management/commands/run_device_listener.py
--------------------------------------------------
Eta ekta long-running process. Machine er sathe connect thake,
ar jokhonই keu finger/card punch kore, SATHE SATHE attendance + SMS
process kore.

CHALANOR niyom (multi-tenant bole tenant/schema dite hobe):

    python manage.py run_device_listener --schema=<school_schema> --device-id=<id>

Example:
    python manage.py run_device_listener --schema=demo_school --device-id=1

Production e eta supervisor / systemd / pm2 diye 24/7 cholbe jate
machine theke kono punch miss na hoy. Connection chhute gele auto-reconnect
kore.

Jodi ekই school e ekadhik machine thake, protita machine er jonno alada
process cholbe (ba --device-id chara dile shob active device er jonno
alada thread).
"""

import time
import logging

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

logger = logging.getLogger('attendance')


class Command(BaseCommand):
    help = "ZKTeco machine er sathe realtime connect thake ar punch hole instant attendance+SMS kore."

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema', required=True,
            help="Je school er (tenant) schema er jonno cholbe."
        )
        parser.add_argument(
            '--device-id', type=int, required=True,
            help="BiometricDevice er id."
        )
        parser.add_argument(
            '--reconnect-delay', type=int, default=10,
            help="Connection chhute gele koto second por abar try korbe."
        )

    def handle(self, *args, **options):
        schema = options['schema']
        device_id = options['device_id']
        reconnect_delay = options['reconnect_delay']

        # import gulo ekhane (schema context er bhitore model use korbo)
        from device.models import BiometricDevice
        from device.zk_client import ZKClient
        from device import services

        # device er punch status code -> source string mapping
        # pyzk Attendance object e .punch / .status thake (device config onujayi)
        SOURCE_MAP = {
            0: 'PASSWORD',
            1: 'FINGER',
            2: 'FINGER',
            3: 'PASSWORD',
            4: 'CARD',
            15: 'FACE',
        }

        self.stdout.write(self.style.SUCCESS(
            f"[{schema}] Device listener cholche... device_id={device_id}"
        ))

        while True:
            client = None
            try:
                with schema_context(schema):
                    device = BiometricDevice.objects.filter(
                        id=device_id, is_active=True
                    ).first()
                    if not device:
                        raise CommandError(
                            f"Active device id={device_id} pawa gelo na ({schema})."
                        )

                client = ZKClient(device)
                conn = client.connect()
                self.stdout.write(self.style.SUCCESS(
                    f"[{schema}] Connected: {device.name} ({device.ip_address})"
                ))

                # live_capture block kore — protita punch e nicher loop cholbe
                for attendance in conn.live_capture():
                    if attendance is None:
                        # timeout tick — connection alive ache kina check
                        continue

                    device_user_id = attendance.user_id
                    punch_time = attendance.timestamp
                    raw_status = getattr(attendance, 'punch', None)
                    if raw_status is None:
                        raw_status = getattr(attendance, 'status', None)
                    source = SOURCE_MAP.get(raw_status, 'UNKNOWN')

                    self.stdout.write(
                        f"[{schema}] PUNCH user_id={device_user_id} "
                        f"time={punch_time} status={raw_status}"
                    )

                    # PROTITA punch — schema context er bhitore process kori
                    try:
                        with schema_context(schema):
                            log = services.process_punch(
                                device_user_id=device_user_id,
                                punch_time=punch_time,
                                device=device,
                                source=source,
                                raw_status=raw_status,
                            )
                        self.stdout.write(self.style.SUCCESS(
                            f"[{schema}] -> {log.person_type} "
                            f"sms_sent={log.sms_sent}"
                        ))
                    except Exception as e:  # noqa
                        logger.exception("Punch process failed: %s", e)
                        self.stderr.write(self.style.ERROR(
                            f"[{schema}] punch process error: {e}"
                        ))

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("\nListener bondho kora holo."))
                break
            except Exception as e:  # noqa
                logger.exception("Device listener error: %s", e)
                self.stderr.write(self.style.ERROR(
                    f"[{schema}] Connection error: {e}. "
                    f"{reconnect_delay}s por abar try korbo..."
                ))
                time.sleep(reconnect_delay)
            finally:
                if client:
                    client.disconnect()
