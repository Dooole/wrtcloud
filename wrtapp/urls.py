from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from wrtapp import views
from wrtapp import provision

urlpatterns = [
	# Devices
	path('device/show', views.deviceView.show),
	path('device/create', views.deviceView.create),
	path('device/edit/<int:id>', views.deviceView.edit),
	path('device/update/<int:id>', views.deviceView.update),
	path('device/delete/<int:id>', views.deviceView.delete),
	# Configuration
	path('configuration/show', views.configView.show),
	path('configuration/edit/<int:id>', views.configView.edit),
	path('configuration/update/<int:id>', views.configView.update),
	# Statistics
	path('statistics/show', views.statsView.show),
	path('statistics/delete/<int:id>', views.statsView.delete),
	# Log
	path('log/show', views.logView.show),
	path('log/delete/<int:id>', views.logView.delete),
	# Provision
	path('provisioning', csrf_exempt(provision.ops.process)),
]
