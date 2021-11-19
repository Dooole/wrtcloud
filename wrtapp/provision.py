import json
import hashlib
import re

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.http import HttpResponseForbidden

from wrtapp.models import Device
from wrtapp.models import Configuration
from wrtapp.models import Statistics
from wrtapp.models import Log

from django.conf import settings

PROV_SCHEMA = {
	'statistics': {
		'system': {
			'mac': r'^([a-fA-F0-9]{2}[:|\-]?){6}$',
			'model': r'^[\w\s\+]+$',
			'cpu_load': r'^\d+\.\d+$',
			'memory_usage': r'^\d+\.\d+$',
			'status': r'^[\w]+$'
		}
	},
	'configuration': {
		'system': {
			'hostname': r'^[\w]+$'
		},
		'network': {
			'ip': r'^([0-9]+[\.]?){4}$',
			'netmask': r'^([0-9]+[\.]?){4}$',
			'gateway': r'^([0-9]+[\.]?){4}$',
			'dns1': r'^([0-9]+[\.]?){4}$',
			'dns2': r'^([0-9]+[\.]?){4}$',
		}
	},
	'token': r'^[a-fA-F0-9]{64}$'
}

def data_is_valid(schema, data):
	for key in schema:
		if key in data:
			if isinstance(schema[key], dict):
				if not isinstance(data[key], dict):
					return False
				elif not data_is_valid(schema[key], data[key]):
					return False
			else:
				if not re.search(schema[key], str(data[key])):
					return False
		else:
			return False
	return True

def token_is_valid(token):
	hash = hashlib.sha256()
	hash.update(bytearray(settings.PROVISIONING_PASSWORD, 'utf8'))

	if hash.hexdigest() != token:
		return False

	return True

def register_device(data):
	st = data['statistics']['system']
	mac = st['mac'].upper()
	try:
		device = Device.objects.get(mac=mac)
	except Device.DoesNotExist:
		device = None
	except:
		return False
	if device:
		# Already registered
		return True

	# Create device entry
	device = Device(
		mac = mac,
		model = st['model'],
		name = 'Generic device',
		description = 'Automatically added'
	)
	try:
		device.save()
	except:
		return False

	# Also create initial config
	cfg = data['configuration']
	config = Configuration(
		device = device,
		hostname = cfg['system']['hostname'],
		ip = cfg['network']['ip'],
		netmask = cfg['network']['netmask'],
		gateway = cfg['network']['gateway'],
		dns1 = cfg['network']['dns1'],
		dns2 = cfg['network']['dns2']
	)
	try:
		config.save()
	except:
		return False

	return True

class ProvisionOperations():
	def process(self, request):
		if request.method == 'POST':
			try:
				jsondata = json.loads(request.body)
			except:
				return HttpResponseBadRequest()

			if not data_is_valid(PROV_SCHEMA, jsondata):
				return HttpResponseBadRequest()

			if not token_is_valid(jsondata['token']):
				return HttpResponseForbidden()

			if not register_device(jsondata):
				return HttpResponseServerError()

			data = json.dumps(jsondata, sort_keys=True, indent=4)
			return HttpResponse(data, content_type='application/json')
		else:
			return HttpResponseBadRequest()

ops = ProvisionOperations()
