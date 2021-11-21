import logging

from wrtapp.models import Log, Device
from django.contrib.auth.models import User

class Logger:
	def __init__(self, name):
		self.logger = logging.getLogger()
		self.logname = name

	def log_message(self, severity, msg, device, user):
		if device and not isinstance(device, Device):
			self.logger.error('logger got non-device arg')
			return
		if user and not isinstance(user, User):
			self.logger.error('logger got non-user arg')
			return
		if not isinstance(msg, str) or not isinstance(severity, str):
			self.logger.error('logger got non-string arg')
			return

		log = Log()
		log.severity = severity
		log.message = msg

		logstr = '[{}]'.format(self.logname.upper())
		if user:
			log.user = user
			logstr = logstr + '[{}]'.format(user.username)
		if device:
			log.device = device
			logstr = logstr + '[{}]'.format(device.mac)
		logstr = logstr + ': {}'.format(msg)

		if severity == 'ERROR':
			try:
				log.save()
			except:
				self.logger.error('failed to log error to db')
			self.logger.error(logstr)
		elif severity == 'WARNING':
			try:
				log.save()
			except:
				self.logger.error('failed to log warning to db')
			self.logger.warning(logstr)
		elif severity == 'DEBUG':
			self.logger.debug(logstr)
		else:
			self.logger.error('invalid severity level')

	def app_error(self, msg, device, user):
		self.log_message('ERROR', msg, device, user)

	def app_warning(self, msg, device, user):
		self.log_message('WARNING', msg, device, user)

	def app_debug(self, msg, device, user):
		self.log_message('DEBUG', msg, device, user)

	def dev_error(self, msg, device):
		self.log_message('ERROR', msg, device, None)

	def dev_warning(self, msg, device):
		self.log_message('WARNING', msg, device, None)

	def dev_debug(self, msg, device):
		self.log_message('DEBUG', msg, device, None)

	def user_error(self, msg, user):
		self.log_message('ERROR', msg, None, user)

	def user_warning(self, msg, user):
		self.log_message('WARNING', msg, None, user)

	def user_debug(self, msg, user):
		self.log_message('DEBUG', msg, None, user)

	def error(self, msg):
		self.log_message('ERROR', msg, None, None)

	def warning(self, msg):
		self.log_message('WARNING', msg, None, None)

	def debug(self, msg):
		self.log_message('DEBUG', msg, None, None)
