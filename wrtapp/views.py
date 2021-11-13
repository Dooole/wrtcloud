from django.shortcuts import render, redirect
from wrtapp.forms import DeviceForm
from wrtapp.models import Device

class DeviceView():
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
		return render(request, 'create.html', {'form': form})

	def show(self, request):
		devices = Device.objects.all()
		return render(request, 'index.html', {'devices': devices})

	def edit(self, request, id):
		device = Device.objects.get(id=id)
		return render(request, 'edit.html', {'device': device})

	def update(self, request, id):
		device = Device.objects.get(id=id)
		form = DeviceForm(request.POST, instance = device)
		if form.is_valid():
			form.save()
			return redirect('/wrtapp/device/show')
		return render(request, 'edit.html', {'device': device})

	def delete(self, request, id):
		device = Device.objects.get(id=id)
		device.delete()
		return redirect('/wrtapp/device/show')

deviceView = DeviceView()
