from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^hello/$', views.index, name='index'),
	url(r'^auth/$', views.authentication, name='auth'),
	url(r'^memcache/$', views.sget_memcache_key_value, name='memcache')
]
