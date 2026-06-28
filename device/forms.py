from django import forms
from .models import BiometricDevice


class BiometricDeviceForm(forms.ModelForm):
    class Meta:
        model = BiometricDevice
        fields = ['name', 'device_type', 'ip_address', 'port', 'password',
                  'force_udp', 'timeout', 'is_exit_device', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Main Gate K40-H'}),
            'device_type': forms.Select(attrs={'class': 'form-select'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.201'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'password': forms.NumberInput(attrs={'class': 'form-control'}),
            'timeout': forms.NumberInput(attrs={'class': 'form-control'}),
            'force_udp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_exit_device': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }