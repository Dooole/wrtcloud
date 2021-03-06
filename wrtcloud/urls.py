"""wrtcloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from wrtapp import views

#every request received by the django framework is tested against series of patterns bellow
#if patern matches, specified handler is called
urlpatterns = [
	path('wrtapp/', include('wrtapp.urls')), #continue url pattern matching in included urls file
	path('wrtapi/', include('wrtapi.urls')), #API module for the mobile app
	re_path(r'^$', views.statsView.show), # show dashboard on empty URI
	re_path(r'^.*$', views.errorsView.notfound), #pattern to match everything rest - not found error handler
]
