from django import forms

from wrtapp.models import Device, Configuration, Statistics, Log
from django.contrib.auth.models import User

class DeviceForm(forms.ModelForm):
	class Meta:
		model = Device
		fields = '__all__'

class ConfigurationForm(forms.ModelForm):
	class Meta:
		model = Configuration
		fields = ['hostname', 'ip', 'netmask', 'gateway', 'dns1', 'dns2']

class UserCreateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password', 'is_superuser']

	def save(self):
		user = User.objects.create_user(
			self.cleaned_data['username'],
			self.cleaned_data['email'],
			self.cleaned_data['password']
		)
		user.is_superuser = self.cleaned_data['is_superuser']
		user.save()

class UserUpdateForm(forms.Form):
	username = forms.CharField()
	email = forms.EmailField()
	password = forms.CharField()
	is_administrator = forms.BooleanField()

