
_author = 'ali.mazouchi'

from django.http import HttpResponse, JsonResponse, QueryDict
from app_db import AppDB
from mem_cache import MemCache
from session import SessionID
import util

import json
import datetime


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def verify_session(request):
	sessionid = util.get_cookie(request, 'sid')
	if sessionid:
		user_data = SessionID.get_session_object(sessionid)
		if not user_data:
			return JsonResponse({'errors':[{'auth': 'cookie expired'}]}, status=401), user_data
	else:
		return JsonResponse({'errors':[{'auth': 'cookie invalid'}]}, status=401), user_data
	return {}, user_data

    
# get json object of data in GET or POST
def get_data_obj(request, user_data=None):
	data_obj = None
	get_obj = request.POST  or request.GET
	if get_obj:
		data_obj = get_obj.get('data')
		if isinstance(data_obj, basestring):
			data_obj = json.loads(data_obj)
	
    # add user_data from database & memcache to request data_obj
	if user_data:
		data_obj['user_data'] = user_data

	return data_obj


def return_jresponse(request, rs):
	# sessionid = util.get_cookie(request, 'sid')
	# util.set_cookie(response, 'sid', sessionid, expire_in_sec=30*60)
	g = request.POST  or request.GET
	cb = g.get('callback')
	if cb:
		rs2 = '%s && %s(%s)' % (cb, cb, json.dumps(rs))
		response = HttpResponse(rs2)
	else:
		response = JsonResponse(rs)
	response['Cache-Control'] = 'no-cache'
	response['Access-Control-Max-Age'] = '1728000'
	response['Access-Control-Allow-Origin'] = '*'
	return response


def authentication(request):
	'''
		authentication of user
		input: key 'data' with value object of:
			'username': user name
			'password': password
			* in case of creating a new account, need to have:
			'act': 'create'  flag to create a new account
			'customer_id': customer id required
			'extra':  object of any other key value information for user 
	'''
	rs = {}
	data_obj = get_data_obj(request)
	if data_obj:
		rs = AppDB.process(data_obj)	# rs: user_data from database

	response = return_jresponse(request, rs)

	# set cookie for valid login
	if rs and not rs.get('err'):	# success of login
		sessionid = SessionID.get_new_session_id(user_data=rs, request=request)
		util.set_cookie(response, 'sid', sessionid, expire_in_sec=30*60)

	return response


def sget_memcache_key_value(request):
	rs, user_data = verify_session(request)
	if rs:
		return rs 	# response
	
	data_obj = get_data_obj(request)
	if data_obj:
		rs = MemCache.process(data_obj)

	return return_jresponse(request, rs)


def file_process(request):
	rs, user_data = verify_session(request)
	if rs:
		return rs 
	
	data_obj = get_data_obj(request)
	if data_obj:
		rs = util.s3_file_process(data_obj)

	return return_jresponse(request, rs)



