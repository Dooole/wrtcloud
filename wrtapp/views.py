import datetime

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User

from wrtapp.forms import DeviceForm
from wrtapp.forms import ConfigurationForm
from wrtapp.forms import UserCreateForm, UserUpdateForm

from wrtapp.models import Device
from wrtapp.models import Configuration
from wrtapp.models import Statistics
from wrtapp.models import Log

from wrtapp.logger import Logger

LOGGER = Logger(__name__)
OFFLINE_THRESHOLD = 60 # Seconds.

class DeviceView:
	def create(self, request):
		if request.method == 'POST':
			form = DeviceForm(request.POST)
			if form.is_valid():
				try:
					form.save()
					return redirect('/wrtapp/device/show')
				except:
					LOGGER.error('Failed to save device form')
			else:
				LOGGER.error('Invalid device form: {}'.format(str(form.errors)))
		else:
			form = DeviceForm()
		return render(request, 'device/create.html', {'form': form})

	def show(self, request):
		devices = Device.objects.all()
		return render(request, 'device/index.html', {'devices': devices})

	def edit(self, request, id):
		device = Device.objects.get(id=id)
		return render(request, 'device/edit.html', {'device': device})

	def update(self, request, id):
		device = Device.objects.get(id=id)
		form = DeviceForm(request.POST, instance = device)
		if form.is_valid():
			try:
				form.save()
				return redirect('/wrtapp/device/show')
			except:
				LOGGER.error('Failed to save device form')
		else:
			LOGGER.error('Invalid device form: {}'.format(str(form.errors)))
		return render(request, 'device/edit.html', {'device': device})

	def delete(self, request, id):
		device = Device.objects.get(id=id)
		try:
			device.delete()
			return redirect('/wrtapp/device/show')
		except:
			LOGGER.error('Failed to delete device')

	def deleteall(self, request):
		try:
			Device.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all devices')
		return redirect('/wrtapp/device/show')

class ConfigurationView:
	def show(self, request):
		configs = Configuration.objects.all()
		return render(request, 'config/index.html', {'configs': configs})

	def edit(self, request, id):
		config = Configuration.objects.get(device_id=id)
		return render(request, 'config/edit.html', {'config': config})

	def update(self, request, id):
		config = Configuration.objects.get(device_id=id)
		form = ConfigurationForm(request.POST, instance = config)
		if form.is_valid():
			try:
				form.save()
				return redirect('/wrtapp/configuration/show')
			except:
				LOGGER.error('Failed to save config form')
		else:
			LOGGER.error('Invalid config form: {}'.format(str(form.errors)))
		return render(request, 'config/edit.html', {'config': config})

def check_status(stat):
	now = datetime.datetime.now(stat.date.tzinfo)
	diff = now - stat.date
	if diff.total_seconds() > OFFLINE_THRESHOLD:
		stat.status = 'OFFLINE'

class StatisticsView:
	def show(self, request):
		stats = Statistics.objects.all()
		for stat in stats:
			check_status(stat)
		return render(request, 'stats/index.html', {'stats': stats})

	def delete(self, request, id):
		stat = Statistics.objects.get(device_id=id)
		try:
			stat.delete()
			return redirect('/wrtapp/statistics/show')
		except:
			LOGGER.error('Failed to delete stats')

	def deleteall(self, request):
		try:
			Statistics.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all statistics')
		return redirect('/wrtapp/statistics/show')

class UserView:
	def create(self, request):
		if request.method == 'POST':
			form = UserCreateForm(request.POST)
			if form.is_valid():
				try:
					# Save form data and show users if OK
					form.save()
					return redirect('/wrtapp/user/show')
				except:
					LOGGER.error('Failed to save user form')
			else:
				LOGGER.error('Invalid user form: {}'.format(str(form.errors)))
		else:
			form = UserCreateForm()
		# Show form again if NOT OK
		return render(request, 'user/create.html', {'form': form})

	def show(self, request):
		users = User.objects.all()
		return render(request, 'user/index.html', {'users': users})

	def edit(self, request, id):
		user = User.objects.get(id=id)
		form = UserUpdateForm(request.POST)
		return render(request, 'user/edit.html', {'form': form})

	def update(self, request, id):
		user = User.objects.get(id=id)
		form = UserUpdateForm(request.POST, instance = user)
		if form.is_valid():
			try:
				# form.save()
				return redirect('/wrtapp/user/show')
			except:
				LOGGER.error('Failed to save user form')
		else:
			LOGGER.error('Invalid user form: {}'.format(str(form.errors)))
		return render(request, 'user/edit.html', {'form': form})

	def delete(self, request, id):
		user = User.objects.get(id=id)
		if user.username == 'admin':
			LOGGER.error('Cannot delete built-in admin user')
			return redirect('/wrtapp/user/show')
		try:
			user.delete()
			return redirect('/wrtapp/user/show')
		except:
			LOGGER.error('Failed to delete user')

class LogView:
	def show(self, request):
		logs = Log.objects.all()
		return render(request, 'log/index.html', {'logs': logs})

	def delete(self, request, id):
		log = Log.objects.get(id=id)
		try:
			log.delete()
			return redirect('/wrtapp/log/show')
		except:
			LOGGER.error('Failed to delete log')

	def deleteall(self, request):
		try:
			Log.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all logs')
		return redirect('/wrtapp/log/show')

class AboutView:
	def show(self, request):
		return render(request, 'about/index.html', {})

class ContactView:
	def show(self, request):
		return render(request, 'contact/index.html', {})

deviceView = DeviceView()
configView = ConfigurationView()
statsView = StatisticsView()
userView = UserView()
logView = LogView()
aboutView = AboutView()
contactView = ContactView()
