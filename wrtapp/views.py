from django.shortcuts import render
from django.shortcuts import redirect

from wrtapp.forms import DeviceForm
from wrtapp.forms import ConfigurationForm

from wrtapp.models import Device
from wrtapp.models import Configuration
from wrtapp.models import Statistics
from wrtapp.models import Log

from wrtapp.logger import Logger

LOGGER = Logger(__name__)

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

class StatisticsView:
	def show(self, request):
		stats = Statistics.objects.all()
		return render(request, 'stats/index.html', {'stats': stats})

	def delete(self, request, id):
		stat = Statistics.objects.get(device_id=id)
		try:
			stat.delete()
			return redirect('/wrtapp/statistics/show')
		except:
			LOGGER.error('Failed to delete stats')

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

deviceView = DeviceView()
configView = ConfigurationView()
statsView = StatisticsView()
logView = LogView()
