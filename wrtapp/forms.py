from django import forms
from wrtapp.models import Device, Configuration, Statistics, Log

class DeviceForm(forms.ModelForm):
	class Meta:
		model = Device
		fields = '__all__'

class ConfigurationForm(forms.ModelForm):
	class Meta:
		model = Configuration
		fields = ['hostname', 'ip', 'netmask', 'gateway', 'dns1', 'dns2']
