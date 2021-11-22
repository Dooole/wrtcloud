from django import forms
from django.contrib.auth.models import User

from wrtapp.models import Device
from wrtapp.models import Configuration

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

# This is a more basic form, detached form specific model.
class UserUpdateForm(forms.Form):
	# Input type text
	username = forms.CharField()
	email = forms.EmailField()
	newpassword = forms.CharField(required = False)
	# Input type checkbox
	is_administrator = forms.BooleanField(required = False)

	def update(self, userData):
		self.initial['username'] = userData['username']
		self.initial['email'] = userData['email']
		self.initial['is_administrator'] = userData['is_administrator']
