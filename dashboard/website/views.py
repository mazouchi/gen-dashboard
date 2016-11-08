from django.http import HttpResponse, JsonResponse, QueryDict
from app_db import AppDB
from mem_cache import MemCache

import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
    
# get json object of data in GET or POST
def get_data_obj(request):
	data_obj = None
	get_obj = request.POST  or request.GET
	if get_obj:
		data_obj = get_obj.get('data')
		if isinstance(data_obj, basestring):
			data_obj = json.loads(data_obj)
	
	return data_obj

def authentication(request):
	rs = {}
	data_obj = get_data_obj(request)
	if data_obj:
		rs = AppDB.process(data_obj)
	return JsonResponse(rs)


def sget_memcache_key_value(request):	# TODO: verify sessionid before processing
	rs = {}
	data_obj = get_data_obj(request)
	if data_obj:
		rs = MemCache.process(data_obj)
	return JsonResponse(rs)
