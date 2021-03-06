from django.db import models #this django module implements sql queries required to manage db . Django apps should use this db api instead of manual sql queries
from django.contrib.auth.models import User

#every class bellow represents data model directly migrated to postgresql db
#and objects of these classes represent an entry in corresponding db table 
#and attribute of the obj represents a field in db 
#

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
	date = models.DateTimeField(auto_now=True)

class Log(models.Model):
	device = models.ForeignKey(
		Device,
		on_delete=models.CASCADE,
		null=True
	)
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		null=True
	)
	severity = models.CharField(max_length=32)
	message = models.CharField(max_length=128)
	date = models.DateTimeField(auto_now_add=True)
