import datetime

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.postgres.search import SearchVector, SearchQuery

from django import forms

from wrtapp.forms import DeviceForm
from wrtapp.forms import ConfigurationForm
from wrtapp.forms import UserCreateForm, UserUpdateForm, SearchForm

from wrtapp.models import Device
from wrtapp.models import Configuration
from wrtapp.models import Statistics
from wrtapp.models import Log

from django.http import HttpResponseForbidden

# Built-in DB module, which uses DB connector to manage DB and provides an API to it.
from django.db import connection
from django.db import reset_queries
from django.db.models import Q

from wrtapp.logger import Logger

LOGGER = Logger(__name__)
OFFLINE_THRESHOLD = 60 # Seconds. # if device does not respond in 60 s marked as offline

# Dump SQL queries to console
def log_sql_query():
	for query in connection.queries:
		LOGGER.debug("SQL: {}".format(query['sql']))
		reset_queries()

#all classes bellow represent specific wrtapp backend module and implements handlers for every url pattern defined in urls.py

#this class is a bit special because it uses django authentification middleware for login and logout implementation
#we only pass arguments to this api and api ensures password verification , session creation and etc
class LoginView:
	def login(self, request):
		failed = False
		if request.method == 'POST':
			form = AuthenticationForm(request, data=request.POST)
			if form.is_valid(): #form obj represents data from html imput fields sent by the browser
				username = form.cleaned_data.get('username')
				password = form.cleaned_data.get('password')
				user = authenticate(username=username, password=password)
				if user:
					login(request, user)
					LOGGER.user_warning('Logged in', user)
					log_sql_query()
					return redirect('/wrtapp/statistics/show')
				else:
					failed = True
					LOGGER.error('Invalid username or password attempt')
			else:
				LOGGER.error('Invalid login form received')
				failed = True

		form = AuthenticationForm()
		log_sql_query()
		return render(request, 'login.html', {'form': form, "failed": failed}) #render is the main method which binds html template with data model. 
		#the last argument to this function is py dict which can be accessed in the template using django template scripting language 


	def logout(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		logout(request)
		return redirect('/wrtapp/login')

class DeviceView:
	def create(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		# We have only 2 types of users, so it's enough to
		# check superuser flag here. However, we should use
		# django authorization/permissions API for this:
		# https://docs.djangoproject.com/en/3.2/topics/auth/default/#permissions-and-authorization
		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		if request.method == 'POST':
			form = DeviceForm(request.POST)
			if form.is_valid():
				try:
					form.save() #save method saves form data to the db via model class
					log_sql_query()
					return redirect('/wrtapp/device/show')
				except:
					LOGGER.error('Failed to save device form')
			else:
				LOGGER.error('Invalid device form: {}'.format(str(form.errors)))
		else:
			form = DeviceForm()
		log_sql_query()
		return render(request, 'device/create.html', {'form': form, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		devices = Device.objects.all()
		log_sql_query()
		return render(request, 'device/index.html', {'devices': devices, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	# Search using built-in posgres search feature
	def search(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if request.method == 'POST':
			form = SearchForm(request.POST)
			if form.is_valid():
				try:
					searchstr = form.cleaned_data.get('search')
					devices = Device.objects.filter(Q(mac__icontains=searchstr) |
						Q(model__icontains=searchstr) |
						Q(name__icontains=searchstr) |
						Q(description__icontains=searchstr))

					log_sql_query()
					return render(request, 'device/index.html', {'devices': devices, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})
				except:
					LOGGER.error('Failed to search')
					log_sql_query()
					return redirect('/wrtapp/device/show')
			else:
				LOGGER.error('Invalid search form: {}'.format(str(form.errors)))
				log_sql_query()
				return redirect('/wrtapp/device/show')
		else:
			LOGGER.error('Search attempt with not a POST')
			log_sql_query()
			return redirect('/wrtapp/device/show')

	def edit(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		device = Device.objects.get(id=id)
		log_sql_query()
		return render(request, 'device/edit.html', {'device': device, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def update(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		device = Device.objects.get(id=id)
		form = DeviceForm(request.POST, instance = device)
		if form.is_valid():
			try:
				form.save()
				log_sql_query()
				return redirect('/wrtapp/device/show')
			except:
				LOGGER.error('Failed to save device form')
		else:
			LOGGER.error('Invalid device form: {}'.format(str(form.errors)))
		log_sql_query()
		return render(request, 'device/edit.html', {'device': device, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def delete(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		device = Device.objects.get(id=id)
		try:
			device.delete()
			log_sql_query()
			return redirect('/wrtapp/device/show')
		except:
			LOGGER.error('Failed to delete device')

	def deleteall(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		try:
			Device.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all devices')
		log_sql_query()
		return redirect('/wrtapp/device/show')

class ConfigurationView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		configs = Configuration.objects.all()
		log_sql_query()
		return render(request, 'config/index.html', {'configs': configs, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def search(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if request.method == 'POST':
			form = SearchForm(request.POST)
			if form.is_valid():
				try:
					searchstr = form.cleaned_data.get('search')
					configs = Configuration.objects.filter(Q(device__mac__icontains=searchstr) |
						Q(hostname__icontains=searchstr) |
						Q(ip__icontains=searchstr) |
						Q(netmask__icontains=searchstr) |
						Q(gateway__icontains=searchstr) |
						Q(dns1__icontains=searchstr) |
						Q(dns2__icontains=searchstr))

					log_sql_query()
					return render(request, 'config/index.html', {'configs': configs, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})
				except:
					LOGGER.error('Failed to search')
					log_sql_query()
					return redirect('/wrtapp/configuration/show')
			else:
				LOGGER.error('Invalid search form: {}'.format(str(form.errors)))
				log_sql_query()
				return redirect('/wrtapp/configuration/show')
		else:
			LOGGER.error('Search attempt with not a POST')
			log_sql_query()
			return redirect('/wrtapp/configuration/show')

	def edit(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		config = Configuration.objects.get(device_id=id)
		log_sql_query()
		return render(request, 'config/edit.html', {'config': config, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def update(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		config = Configuration.objects.get(device_id=id)
		form = ConfigurationForm(request.POST, instance = config)
		if form.is_valid():
			try:
				form.save()
				log_sql_query()
				return redirect('/wrtapp/configuration/show')
			except:
				LOGGER.error('Failed to save config form')
		else:
			LOGGER.error('Invalid config form: {}'.format(str(form.errors)))
		log_sql_query()
		return render(request, 'config/edit.html', {'config': config, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

def check_status(stat):
	now = datetime.datetime.now(stat.date.tzinfo)
	diff = now - stat.date
	if diff.total_seconds() > OFFLINE_THRESHOLD:
		stat.status = 'OFFLINE'
		stat.save()

class StatisticsView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		stats = Statistics.objects.all()
		for stat in stats:
			check_status(stat)
		log_sql_query()
		return render(request, 'stats/index.html', {'stats': stats, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def search(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if request.method == 'POST':
			form = SearchForm(request.POST)
			if form.is_valid():
				try:
					searchstr = form.cleaned_data.get('search')
					stats = Statistics.objects.filter(Q(device__mac__icontains=searchstr) |
						Q(status__icontains=searchstr) |
						Q(cpu_load__icontains=searchstr) |
						Q(memory_usage__icontains=searchstr))

					log_sql_query()
					return render(request, 'stats/index.html', {'stats': stats, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})
				except:
					LOGGER.error('Failed to search')
					log_sql_query()
					return redirect('/wrtapp/statistics/show')
			else:
				LOGGER.error('Invalid search form: {}'.format(str(form.errors)))
				log_sql_query()
				return redirect('/wrtapp/statistics/show')
		else:
			LOGGER.error('Search attempt with not a POST')
			log_sql_query()
			return redirect('/wrtapp/statistics/show')

	def delete(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		stat = Statistics.objects.get(device_id=id)
		try:
			stat.delete()
			log_sql_query()
			return redirect('/wrtapp/statistics/show')
		except:
			LOGGER.error('Failed to delete stats')

	def deleteall(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		try:
			Statistics.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all statistics')
		log_sql_query()
		return redirect('/wrtapp/statistics/show')

class UserView:
	def create(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		if request.method == 'POST':
			form = UserCreateForm(request.POST)
			if form.is_valid():
				try:
					user = User.objects.create_user(
						form.cleaned_data['username'],
						form.cleaned_data['email'],
						form.cleaned_data['password']
					)
					user.is_superuser = form.cleaned_data['is_superuser']
					user.save()
					log_sql_query()
					return redirect('/wrtapp/user/show')
				except:
					LOGGER.error('Failed to save user form')
			else:
				LOGGER.error('Invalid user form: {}'.format(str(form.errors)))
		else:
			form = UserCreateForm()
		# Show form again if NOT OK
		log_sql_query()
		return render(request, 'user/create.html', {'form': form, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		users = User.objects.all()
		log_sql_query()
		return render(request, 'user/index.html', {'users': users, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def search(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if request.method == 'POST':
			form = SearchForm(request.POST)
			if form.is_valid():
				try:
					searchstr = form.cleaned_data.get('search')
					users = User.objects.filter(Q(username__icontains=searchstr) | Q(email__icontains=searchstr))
					log_sql_query()
					return render(request, 'user/index.html', {'users': users, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})
				except:
					LOGGER.error('Failed to search')
					log_sql_query()
					return redirect('/wrtapp/user/show')
			else:
				LOGGER.error('Invalid search form: {}'.format(str(form.errors)))
				log_sql_query()
				return redirect('/wrtapp/user/show')
		else:
			LOGGER.error('Search attempt with not a POST')
			log_sql_query()
			return redirect('/wrtapp/user/show')

	def edit(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		user = User.objects.get(id=id)
		# Protect password hash leak - wrap data
		userData = {
			'username': user.username,
			'email': user.email,
			'is_administrator': user.is_superuser,
		}
		form = UserUpdateForm()
		form.update(userData)
		log_sql_query()
		return render(request, 'user/edit.html', {'form': form, 'userId': user.id, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def update(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		if request.method == 'POST':
			user = User.objects.get(id=id)
			form = UserUpdateForm(request.POST)
			if form.is_valid():
				try:
					user.username = form.cleaned_data['username']
					user.email = form.cleaned_data['email']
					user.is_superuser = form.cleaned_data['is_administrator']
					if len(form.cleaned_data['newpassword']) > 0:
						try:
							user.set_password(form.cleaned_data['newpassword'])
						except:
							LOGGER.error('Invalid password format', user)
						LOGGER.user_warning('Changed password', user)
					user.save()
					log_sql_query()
					return redirect('/wrtapp/user/show')
				except:
					LOGGER.error('Failed to save user form')
			else:
				LOGGER.error('Invalid user form: {}'.format(str(form.errors)))
		else:
			form = UserUpdateForm()
		log_sql_query()
		return render(request, 'user/edit.html', {'form': form, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def delete(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		user = User.objects.get(id=id)
		if user.username == 'admin':
			LOGGER.error('Cannot delete built-in admin user')
			log_sql_query()
			return redirect('/wrtapp/user/show')
		try:
			user.delete()
			log_sql_query()
			return redirect('/wrtapp/user/show')
		except:
			LOGGER.error('Failed to delete user')

class LogView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		logs = Log.objects.all()
		log_sql_query()
		return render(request, 'log/index.html', {'logs': logs, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

	def search(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if request.method == 'POST':
			form = SearchForm(request.POST)
			if form.is_valid():
				try:
					searchstr = form.cleaned_data.get('search')
					logs = Log.objects.filter(Q(device__mac__icontains=searchstr) |
						Q(user__username__icontains=searchstr) |
						Q(severity__icontains=searchstr) |
						Q(message__icontains=searchstr))

					log_sql_query()
					return render(request, 'log/index.html', {'logs': logs, 'is_administrator': request.user.is_superuser, 'current_user': request.user.username})
				except:
					LOGGER.error('Failed to search')
					log_sql_query()
					return redirect('/wrtapp/log/show')
			else:
				LOGGER.error('Invalid search form: {}'.format(str(form.errors)))
				log_sql_query()
				return redirect('/wrtapp/log/show')
		else:
			LOGGER.error('Search attempt with not a POST')
			log_sql_query()
			return redirect('/wrtapp/log/show')

	def delete(self, request, id):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		log = Log.objects.get(id=id)
		try:
			log.delete()
			log_sql_query()
			return redirect('/wrtapp/log/show')
		except:
			LOGGER.error('Failed to delete log')

	def deleteall(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		try:
			Log.objects.all().delete()
		except:
			LOGGER.error('Failed to delete all logs')
		log_sql_query()
		return redirect('/wrtapp/log/show')

class ToolsView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		if not request.user.is_superuser:
			return redirect('/wrtapp/errors/forbidden')

		return render(request, 'tools/index.html', {'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

class AboutView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		return render(request, 'about/index.html', {'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

class ContactView:
	def show(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		return render(request, 'contact/index.html', {'is_administrator': request.user.is_superuser, 'current_user': request.user.username})

class ErrorsView:
	def notfound(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		return render(request, 'errors/notfound.html', {'current_user': request.user.username}, status=404)

	def forbidden(self, request):
		if not request.user.is_authenticated:
			return redirect('/wrtapp/login')

		return render(request, 'errors/forbidden.html', {'current_user': request.user.username}, status=403)

#these obj are used to call request handler in urls.py
loginView = LoginView()
deviceView = DeviceView()
configView = ConfigurationView()
statsView = StatisticsView()
userView = UserView()
logView = LogView()
toolsView = ToolsView()
aboutView = AboutView()
contactView = ContactView()
errorsView = ErrorsView()
