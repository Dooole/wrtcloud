from django.urls import path
from wrtapp import views

urlpatterns = [
	# Devices
	path('device/show', views.deviceView.show),
	path('device/create', views.deviceView.create),
	path('device/edit/<int:id>', views.deviceView.edit),
	path('device/update/<int:id>', views.deviceView.update),
	path('device/delete/<int:id>', views.deviceView.delete),
]
