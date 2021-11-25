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

from wrtapp.logger import Logger

from django.conf import settings

#reference dict which defines correct provisioning request structure and value formats
PROV_SCHEMA = {
	'statistics': {
		'system': {
			'mac': r'^([a-fA-F0-9]{2}[:|\-]?){6}$',
			'model': r'^[\w\s\+\.\-]+$',
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

#obj to log errors/warnings/debugs to db log table and system console (foreground mode)
LOGGER = Logger(__name__)

def data_is_valid(schema, data): #checks agent data against schema
	for key in schema:
		if key in data:
			if isinstance(schema[key], dict):
				if not isinstance(data[key], dict):
					LOGGER.error('No dict required by schema: {}'.format(key))
					return False
				elif not data_is_valid(schema[key], data[key]): #calls itself recursively for internal nested dicts
					return False
			else:
				if not re.search(schema[key], str(data[key])): #checks if value matches regular excpresion from the schema
					LOGGER.error('Invalid value by schema: {}'.format(str(data[key])))
					return False
		else:
			LOGGER.error('No key required by schema: {}'.format(key))
			return False
	return True

def token_is_valid(token):
	hash = hashlib.sha256()
	hash.update(bytearray(settings.PROVISIONING_PASSWORD, 'utf8'))

	if hash.hexdigest() != token:
		LOGGER.error('Password hash mismatch')
		return False

	return True

def register_device(data): #if devices does not exsist in db it makes initial table entry for device and config tables
	reqst = data['statistics']['system']
	mac = reqst['mac'].upper()
	try:
		device = Device.objects.get(mac=mac) #obj which directly represents db device table
	except Device.DoesNotExist:
		device = None
	except:
		LOGGER.error('Failed to get device for register')
		return False
	if device:
		LOGGER.dev_debug('Device already exists', device)
		return True

	device = Device( #creates initial device table entry in a form of Device class new object
		mac = mac,
		model = reqst['model'],
		name = 'Generic device',
		description = 'Automatically added'
	)
	try:
		device.save() #saves device obj to db
		LOGGER.dev_warning('Added new device', device)
	except:
		LOGGER.dev_error('Failed to save device', device)
		return False

	LOGGER.dev_debug('Initializing config', device)
	cfg = data['configuration']
	config = Configuration(#creates initial config table entry in a form of Configuration class new object
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
		LOGGER.dev_error('Failed to save config', device)
		return False

	return True

def update_stats(data):
	reqst = data['statistics']['system']
	mac = reqst['mac'].upper()
	try:
		device = Device.objects.get(mac=mac)
	except:
		LOGGER.error('Failed to get device for stats')
		return False

	try:
		stat = Statistics.objects.get(device_id=device.id) # searches for device statistics entry in db using onetoone device and stats relation
	except Statistics.DoesNotExist:
		stat = None
	except:
		LOGGER.dev_error('Failed to get stats', device)
		return False

	if stat: #update exsisting stats
		LOGGER.dev_debug('Updating stats', device)
		stat.status = reqst['status']
		stat.cpu_load = reqst['cpu_load']
		stat.memory_usage = reqst['memory_usage']
	else: #cretae new stats
		LOGGER.dev_debug('Creating stats', device)
		stat = Statistics( #represents stats db table
			device = device,
			status = reqst['status'],
			cpu_load = reqst['cpu_load'],
			memory_usage = reqst['memory_usage']
		)

	try:
		stat.save()
	except:
		LOGGER.dev_error('Failed to save stats', device)
		return False

	return True

def build_config(data): #if db config is different from the config send by agent this function forms py dict from db config 
	reqst = data['statistics']['system']
	reqcfg_sys = data['configuration']['system']# variable pointing to system config dict directly
	reqcfg_net = data['configuration']['network']# variable pointing to network config dict directly

	mac = reqst['mac'].upper()
	try:
		device = Device.objects.get(mac=mac)
	except:
		LOGGER.error('Failed to get device for config')
		return None

	try:
		dbcfg = Configuration.objects.get(device_id=device.id) ## searches for device config entry in db using onetoone device and config relation
	except:
		LOGGER.dev_error('Failed to get config', device)
		return None

	changed = False
	cfgdata = {'config_status': 'UNCHANGED'} #initial dict used to respond to agent request
	cfg = {}

	#all following six if statements checks if specific config parameter in db has changed and adds it to response dict if it has changed
	if reqcfg_sys['hostname'] != dbcfg.hostname:
		#this item exsistence check in extra 'cfg' dict is required to ensure that final dict contains only changed values
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

	if changed: #if any of the six config key above changed add 'configuration' obj to the final response dict 
	#also set config status to change
		LOGGER.dev_debug('Config changed', device)
		cfgdata['config_status'] = 'CHANGED'
		cfgdata['configuration'] = cfg

	return cfgdata

class ProvisionOperations: #single class which implements device authentification, registration and configuration
	def process(self, request):
		if request.method == 'POST':
			try:
				reqjson = json.loads(request.body) #deserializes agent post data into py dict
			except:
				LOGGER.error('Failed to deserialize post')
				return HttpResponseBadRequest()

			if not data_is_valid(PROV_SCHEMA, reqjson): #verifies if data has required(by reference schema) structure and values
				LOGGER.error('Invalid post data')
				return HttpResponseBadRequest()

			if not token_is_valid(reqjson['token']): #verifies if agent token is valid(passw correct)
				LOGGER.error('Invalid security token')
				return HttpResponseForbidden()

			if not register_device(reqjson):
				LOGGER.error('Failed to register device') #if device is not in db this funtion adds initial device and config table entry
				return HttpResponseServerError()

			if not update_stats(reqjson):
				LOGGER.error('Failed to update stats')#updates device stats entry
				return HttpResponseServerError()

			config = build_config(reqjson) #checks if agent config has changed in db and builts config py dict if it has 
			if config:
				try: # serializes changed configuration and sends to agent
					respdata = json.dumps(config, sort_keys=True, indent=4)
				except:
					LOGGER.error('Failed to serialize config')
					return HttpResponseServerError()
				return HttpResponse(respdata, content_type='application/json')
			else: #failed to built config
				LOGGER.error('Config was not found')
				return HttpResponseNotFound()
		else:
			LOGGER.error('Received not a POST request')
			return HttpResponseBadRequest()

ops = ProvisionOperations() #this obj is used by  urls.py as a provisioning url handler
