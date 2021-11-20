from django.shortcuts import render, redirect
from wrtapp.forms import DeviceForm, ConfigurationForm
from wrtapp.models import Device, Configuration, Statistics, Log

class DeviceView:
	def create(self, request):
		if request.method == 'POST':
			form = DeviceForm(request.POST)
			if form.is_valid():
				try:
					form.save()
					return redirect('/wrtapp/device/show')
				except:
					pass
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
			form.save()
			return redirect('/wrtapp/device/show')
		return render(request, 'device/edit.html', {'device': device})

	def delete(self, request, id):
		device = Device.objects.get(id=id)
		device.delete()
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
			form.save()
			return redirect('/wrtapp/configuration/show')
		else:
			print(form.errors)
		return render(request, 'config/edit.html', {'config': config})

class StatisticsView:
	def show(self, request):
		stats = Statistics.objects.all()
		return render(request, 'stats/index.html', {'stats': stats})

	def delete(self, request, id):
		stat = Statistics.objects.get(device_id=id)
		stat.delete()
		return redirect('/wrtapp/statistics/show')

class LogView:
	def show(self, request):
		logs = Log.objects.all()
		return render(request, 'log/index.html', {'logs': logs})

	def delete(self, request, id):
		log = Log.objects.get(id=id)
		log.delete()
		return redirect('/wrtapp/log/show')

deviceView = DeviceView()
configView = ConfigurationView()
statsView = StatisticsView()
logView = LogView()
