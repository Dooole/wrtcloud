#!/usr/bin/env python3

import json
import hashlib
import logging
import time
import random

from http.client import HTTPConnection

#sames as agent but imitates requests by incrementing index 
CTX = {
	"timeout": 10, # Seconds.
	"interval": 1, # Seconds.
	"server": "192.168.1.79",
	"port": 8000,
	"password": "yJAFruh5RTuMVpvxRvc7xOBFGTrB3abd"
}

class Statistics:
	def __init__(self, idx):
		self.idx = idx

	def get(self):
		stats = {
			"system": {
				"model": "SIM{}".format(str(self.idx)),
				"status": "OK",
				"mac": "{:02d}:{:02d}:{:02d}:{:02d}:{:02d}:{:02d}".format(self.idx, self.idx, self.idx, self.idx, self.idx, self.idx),
				"cpu_load": round(random.uniform(10.0, 30.0),1),
				"memory_usage": round(random.uniform(40.0, 50.0),1),
			}
		}
		return stats

class Configuration:
	def __init__(self, idx):
		self.idx = idx

	def get(self):
		config = {
			"system": {
				"hostname": "sim{}".format(str(self.idx)),
			},
			"network": {
				"ip": "{}.{}.{}.{}".format(str(self.idx), str(self.idx), str(self.idx), str(self.idx)),
				"netmask": "{}.{}.{}.{}".format(str(self.idx), str(self.idx), str(self.idx), str(self.idx)),
				"gateway": "{}.{}.{}.{}".format(str(self.idx), str(self.idx), str(self.idx), str(self.idx)),
				"dns1": "{}.{}.{}.{}".format(str(self.idx), str(self.idx), str(self.idx), str(self.idx)),
				"dns2": "{}.{}.{}.{}".format(str(self.idx), str(self.idx), str(self.idx), str(self.idx)),
			}
		}
		return config

def server_send(datadict):
	try:
		reqdata = json.dumps(datadict).encode("utf-8")
	except:
		logging.error("Failed to serialize request data")
		return None

	headers = {"Content-type": "application/json"}
	conn = HTTPConnection(CTX["server"], CTX["port"], CTX["timeout"])
	try:
		conn.request("POST", "/wrtapp/provisioning", reqdata, headers)
	except:
		logging.error("Failed to send request")
		conn.close()
		return None

	response = conn.getresponse()
	if response.status != 200:
		logging.error("Server returned error: {}".format(str(response.status)))
		conn.close()
		return None

	respdata = response.read()
	if not respdata:
		logging.error("Failed to read response data")
		conn.close()
		return None

	conn.close()
	try:
		resp = json.loads(respdata.decode("utf-8"))
		return resp
	except:
		logging.error("Failed to deserialize response data")
		return None

def calculate_token():
	hash = hashlib.sha256()
	hash.update(bytearray(CTX["password"], "utf8"))
	return hash.hexdigest()

def provisioning_sync(idx):
	config = Configuration(idx)
	stats = Statistics(idx)

	reqdict = {
		"statistics": stats.get(),
		"configuration": config.get(),
		"token": calculate_token(),
	}

	server_send(reqdict)

def simulation_run():
	try:
		while True:
			for idx in range(1, 28):
				logging.warning("Simulating client {}".format(str(idx)))
				provisioning_sync(idx)
				time.sleep(CTX["interval"])

	except KeyboardInterrupt:
		logging.warning("Interrupted!")

simulation_run()
