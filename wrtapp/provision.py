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
	reqst = data['statistics']['system']
	mac = reqst['mac'].upper()
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
		model = reqst['model'],
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

def update_stats(data):
	reqst = data['statistics']['system']
	mac = reqst['mac'].upper()
	try:
		device = Device.objects.get(mac=mac)
	except:
		# Device must exist.
		return False

	try:
		stat = Statistics.objects.get(device_id=device.id)
	except Statistics.DoesNotExist:
		stat = None
	except:
		# Other failure.
		return False

	if stat:
		# Update existing stats.
		stat.status = reqst['status']
		stat.cpu_load = reqst['cpu_load']
		stat.memory_usage = reqst['memory_usage']
	else:
		# Create new stats.
		stat = Statistics(
			device = device,
			status = reqst['status'],
			cpu_load = reqst['cpu_load'],
			memory_usage = reqst['memory_usage']
		)

	try:
		stat.save()
	except:
		return False

	return True

def build_config(data):
	reqst = data['statistics']['system']
	reqcfg_sys = data['configuration']['system']
	reqcfg_net = data['configuration']['network']

	mac = reqst['mac'].upper()
	try:
		device = Device.objects.get(mac=mac)
	except:
		return None

	try:
		dbcfg = Configuration.objects.get(device_id=device.id)
	except:
		return None

	changed = False
	cfgdata = {'config_status': 'UNCHANGED'}
	cfg = {}

	if reqcfg_sys['hostname'] != dbcfg.hostname:
		if not 'system' in cfg:
			cfg['system'] = {}
		cfg['system']['hostname'] = dbcfg.hostname
		changed = True

	if reqcfg_net['ip'] != dbcfg.ip:
		if not 'network' in cfg:
			cfg['network'] = {}
		cfg['network']['ip'] = dbcfg.ip
		changed = True

	if reqcfg_net['netmask'] != dbcfg.netmask:
		if not 'network' in cfg:
			cfg['network'] = {}
		cfg['network']['netmask'] = dbcfg.netmask
		changed = True

	if reqcfg_net['gateway'] != dbcfg.gateway:
		if not 'network' in cfg:
			cfg['network'] = {}
		cfg['network']['gateway'] = dbcfg.gateway
		changed = True

	if reqcfg_net['dns1'] != dbcfg.dns1:
		if not 'network' in cfg:
			cfg['network'] = {}
		cfg['network']['dns1'] = dbcfg.dns1
		changed = True

	if reqcfg_net['dns2'] != dbcfg.dns2:
		if not 'network' in cfg:
			cfg['network'] = {}
		cfg['network']['dns2'] = dbcfg.dns2
		changed = True

	if changed:
		cfgdata['config_status'] = 'CHANGED'
		cfgdata['configuration'] = cfg

	return cfgdata

class ProvisionOperations:
	def process(self, request):
		if request.method == 'POST':
			try:
				reqjson = json.loads(request.body)
			except:
				return HttpResponseBadRequest()

			if not data_is_valid(PROV_SCHEMA, reqjson):
				return HttpResponseBadRequest()

			if not token_is_valid(reqjson['token']):
				return HttpResponseForbidden()

			if not register_device(reqjson):
				return HttpResponseServerError()

			if not update_stats(reqjson):
				return HttpResponseServerError()

			config = build_config(reqjson)
			if config:
				try:
					respdata = json.dumps(config, sort_keys=True, indent=4)
				except:
					return HttpResponseServerError()
				return HttpResponse(respdata, content_type='application/json')
			else:
				return HttpResponseNotFound()
		else:
			return HttpResponseBadRequest()

ops = ProvisionOperations()
