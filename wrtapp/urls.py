from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from wrtapp import views
from wrtapp import provision

urlpatterns = [ #url patterns specific to wrtapp django application
	# Login and logout
	path('login', views.loginView.login),
	path('logout', views.loginView.logout),
	# Devices
	path('device/show', views.deviceView.show),
	path('device/create', views.deviceView.create),
	path('device/edit/<int:id>', views.deviceView.edit),
	path('device/update/<int:id>', views.deviceView.update),
	path('device/delete/<int:id>', views.deviceView.delete),
	path('device/deleteall', views.deviceView.deleteall),
	# Configuration
	path('configuration/show', views.configView.show),
	path('configuration/edit/<int:id>', views.configView.edit),
	path('configuration/update/<int:id>', views.configView.update),
	# Statistics
	path('statistics/show', views.statsView.show),
	path('statistics/delete/<int:id>', views.statsView.delete),
	path('statistics/deleteall', views.statsView.deleteall),
	# User
	path('user/show', views.userView.show),
	path('user/create', views.userView.create),
	path('user/edit/<int:id>', views.userView.edit),
	path('user/update/<int:id>', views.userView.update),
	path('user/delete/<int:id>', views.userView.delete),
	# Log
	path('log/show', views.logView.show),
	path('log/delete/<int:id>', views.logView.delete),
	path('log/deleteall', views.logView.deleteall),
	# About
	path('about/show', views.aboutView.show),
	# Contact
	path('contact/show', views.contactView.show),
	# Provision
	path('provisioning', csrf_exempt(provision.ops.process)),
]
