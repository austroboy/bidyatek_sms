"""
device/management/commands/sync_device_attendance.py
----------------------------------------------------
Jodi listener bondho thaka obosthay keu punch kore, segulo device er
memory te joma thake. Ei command device theke shob record tene ene
process kore (jegulo age process hoy nai).

Cron diye proti 5-10 min por chalano jete pare backup hisebe:

    python manage.py sync_device_attendance --schema=<school_schema> --device-id=<id>

Note: Eta backup. Asol instant SMS ta listener kore. Tobe sync er somoy
purono punch er o SMS pathate na chaile --no-sms diye chalano jay.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

logger = logging.getLogger('attendance')


class Command(BaseCommand):
    help = "Device memory theke joma attendance record tene ene process kore."

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True)
        parser.add_argument('--device-id', type=int, required=True)
        parser.add_argument(
            '--clear', action='store_true',
            help="Process howar por device er record muche debe."
        )
        parser.add_argument(
            '--no-sms', action='store_true',
            help="Purono record gulor jonno SMS pathabe na (recommended)."
        )

    def handle(self, *args, **options):
        schema = options['schema']
        device_id = options['device_id']

        from device.models import BiometricDevice, DevicePunchLog
        from device.zk_client import ZKClient
        from device import services

        with schema_context(schema):
            device = BiometricDevice.objects.filter(id=device_id).first()
            if not device:
                raise CommandError(f"Device {device_id} pawa gelo na.")

        client = ZKClient(device)
        try:
            conn = client.connect()
            conn.disable_device()  # sync er somoy machine off rakha bhalo
            records = conn.get_attendance()
            self.stdout.write(f"Device e {len(records)} ta record paoa gelo.")

            SOURCE_MAP = {0: 'PASSWORD', 1: 'FINGER', 2: 'FINGER',
                          3: 'PASSWORD', 4: 'CARD', 15: 'FACE'}

            processed = 0
            for att in records:
                raw_status = getattr(att, 'punch', None)
                if raw_status is None:
                    raw_status = getattr(att, 'status', None)
                source = SOURCE_MAP.get(raw_status, 'UNKNOWN')

                with schema_context(schema):
                    # duplicate already-processed gulo services er bhitore
                    # unique_together diye guard kora ache
                    if options['no_sms']:
                        # SMS chara — sudhu attendance bosabo
                        self._process_no_sms(
                            services, att.user_id, att.timestamp,
                            device, source, raw_status
                        )
                    else:
                        services.process_punch(
                            device_user_id=att.user_id,
                            punch_time=att.timestamp,
                            device=device,
                            source=source,
                            raw_status=raw_status,
                        )
                processed += 1

            self.stdout.write(self.style.SUCCESS(f"{processed} ta process holo."))

            if options['clear']:
                conn.clear_attendance()
                self.stdout.write(self.style.WARNING("Device record clear kora holo."))

            conn.enable_device()
            with schema_context(schema):
                from django.utils import timezone
                device.last_sync = timezone.now()
                device.save(update_fields=['last_sync'])

        finally:
            client.disconnect()

    def _process_no_sms(self, services, user_id, punch_time, device, source, raw_status):
        """SMS chhara version — _dispatch_sms ke bypass kore."""
        import device.services as svc
        original = svc._dispatch_sms
        svc._dispatch_sms = lambda *a, **k: (False, "sms skipped (sync)")
        try:
            services.process_punch(
                device_user_id=user_id, punch_time=punch_time,
                device=device, source=source, raw_status=raw_status,
            )
        finally:
            svc._dispatch_sms = original
