"""
device/views.py
---------------
Chhoto control panel + ekta optional ADMS push webhook.

Duito poth ache ZKTeco machine theke data anar:

  (A) PULL mode (recommended ekhane): amra machine er sathe connect kore
      live_capture/get_attendance kori. Eta run_device_listener command kore.
      Ei file er test_connection / trigger_sync ei mode er jonno.

  (B) PUSH mode (ADMS/iclock): kichu firmware e machine NIJE server e HTTP
      POST kore. Sei khetre nicher device_push_webhook lage. K40-H er
      firmware e jodi "ADMS"/"Cloud server" option thake tahole eta use
      kora jay (machine e ei server er URL+port boshate hoy).

Apnar prothom integration er jonno (A) i jthesto. (B) ta bonus rakhlam.
"""

import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BiometricDeviceForm
from .models import BiometricDevice
from .zk_client import ZKClient
from . import services

logger = logging.getLogger('attendance')


@login_required(login_url='login')
def device_list(request):
    devices = BiometricDevice.objects.all()
    return render(request, 'device/device_list.html', {'devices': devices})


@login_required(login_url='login')
def test_connection(request, device_id):
    device = get_object_or_404(BiometricDevice, id=device_id)
    client = ZKClient(device)
    try:
        conn = client.connect()
        info = {
            'firmware': conn.get_firmware_version(),
            'serial': conn.get_serialnumber(),
            'users': len(conn.get_users()),
        }
        client.disconnect()
        return JsonResponse({'status': 'ok', 'info': info})
    except Exception as e:  # noqa
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)


@login_required(login_url='login')
def trigger_sync(request, device_id):
    """
    Browser theke ek click e device er joma record tene ene process kore.
    (Background e management command cholle eta lage na, eta manual backup.)
    """
    device = get_object_or_404(BiometricDevice, id=device_id)
    client = ZKClient(device)
    SOURCE_MAP = {0: 'PASSWORD', 1: 'FINGER', 2: 'FINGER',
                  3: 'PASSWORD', 4: 'CARD', 15: 'FACE'}
    try:
        conn = client.connect()
        conn.disable_device()
        records = conn.get_attendance()
        count = 0
        for att in records:
            raw_status = getattr(att, 'punch', None)
            if raw_status is None:
                raw_status = getattr(att, 'status', None)
            services.process_punch(
                device_user_id=att.user_id,
                punch_time=att.timestamp,
                device=device,
                source=SOURCE_MAP.get(raw_status, 'UNKNOWN'),
                raw_status=raw_status,
            )
            count += 1
        conn.enable_device()
        client.disconnect()
        messages.success(request, f'{count} ta record sync holo.')
    except Exception as e:  # noqa
        messages.error(request, f'Sync error: {e}')
    return redirect('device_list')


# ---------------------------------------------------------------------------
# (B) OPTIONAL: ZKTeco ADMS / iClock PUSH protocol webhook
# ---------------------------------------------------------------------------
@csrf_exempt
def device_push_webhook(request):
    """
    Kichu ZKTeco firmware NIJE server e data POST kore (iclock protocol).
    Machine er settings e Comm > Cloud Server / ADMS te ei URL set korte hoy.

    Handshake (GET): machine prothome /iclock/cdata?SN=xxx GET kore.
    Data (POST): ATTLOG record gulo tab-separated text e POST kore:
        user_id <tab> timestamp <tab> status <tab> verify <tab> ...

    NOTE: Eta multi-tenant. Machine er SN ba domain diye tenant ber korte
    hobe. Ekhane simple version dilam — production e SN -> tenant mapping
    ekta SHARED table e rakhte hobe. Apnar prothom kaj e (A) mode use korun;
    ei webhook lagle pore configure korben.
    """
    if request.method == 'GET':
        # handshake — machine ke OK bolte hoy
        return HttpResponse("OK")

    if request.method == 'POST':
        SOURCE_MAP = {'0': 'PASSWORD', '1': 'FINGER', '4': 'CARD', '15': 'FACE'}
        body = request.body.decode('utf-8', errors='ignore')
        lines = [l for l in body.splitlines() if l.strip()]
        processed = 0
        for line in lines:
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            device_user_id = parts[0].strip()
            timestamp_str = parts[1].strip()
            status_code = parts[2].strip() if len(parts) > 2 else ''
            try:
                from datetime import datetime
                punch_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
            services.process_punch(
                device_user_id=device_user_id,
                punch_time=punch_time,
                device=None,  # SN diye device ber kora jay — pore add korben
                source=SOURCE_MAP.get(status_code, 'UNKNOWN'),
                raw_status=int(status_code) if status_code.isdigit() else None,
            )
            processed += 1
        return HttpResponse(f"OK: {processed}")

    return HttpResponse("OK")

@login_required(login_url='login')
def device_add(request):
    if request.method == 'POST':
        form = BiometricDeviceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Device add holo.')
            return redirect('device_list')
    else:
        form = BiometricDeviceForm()
    return render(request, 'device/device_form.html', {'form': form, 'title': 'Add Device'})


@login_required(login_url='login')
def device_edit(request, device_id):
    device = get_object_or_404(BiometricDevice, id=device_id)
    if request.method == 'POST':
        form = BiometricDeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, 'Device update holo.')
            return redirect('device_list')
    else:
        form = BiometricDeviceForm(instance=device)
    return render(request, 'device/device_form.html', {'form': form, 'title': 'Edit Device'})


@login_required(login_url='login')
def device_delete(request, device_id):
    get_object_or_404(BiometricDevice, id=device_id).delete()
    messages.success(request, 'Device delete holo.')
    return redirect('device_list')