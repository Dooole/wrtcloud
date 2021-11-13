from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
	mac = models.CharField(max_length=32)
	model = models.CharField(max_length=64)
	name = models.CharField(max_length=64)
	description = models.CharField(max_length=128)
	date_added = models.DateTimeField(auto_now_add=True)

class Configuration(models.Model):
	device = models.OneToOneField(
		Device,
		on_delete=models.CASCADE,
		primary_key=True,
	)
	hostname = models.CharField(max_length=64)
	ip = models.GenericIPAddressField(protocol='IPv4')
	netmask = models.GenericIPAddressField(protocol='IPv4')
	gateway = models.GenericIPAddressField(protocol='IPv4')
	dns1 = models.GenericIPAddressField(protocol='IPv4')
	dns2 = models.GenericIPAddressField(protocol='IPv4')

class Statistics(models.Model):
	device = models.OneToOneField(
		Device,
		on_delete=models.CASCADE,
		primary_key=True,
	)
	status = models.CharField(max_length=32)
	cpu_load = models.FloatField()
	memory_usage = models.FloatField()

class Log(models.Model):
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE
	)
	severity = models.CharField(max_length=32)
	message = models.CharField(max_length=128)
	date = models.DateTimeField(auto_now_add=True)
