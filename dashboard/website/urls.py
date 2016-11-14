from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
	url(r'^hello/$', views.index, name='index'),
	url(r'^auth/$', views.authentication, name='auth'),
	url(r'^memcache/$', views.sget_memcache_key_value, name='memcache'),
	url(r'^file/$', views.file_process, name='file'),
	url(r'^page/$', TemplateView.as_view(template_name='page.html'))
]
