
_author = 'ali.mazouchi'

import copy
import json
import time
import hashlib

import util
from mem_cache import MemCache



class SessionID(object):
 	"""
 		provide a session id for connection and also verify session ids
 	"""
 	__mc_prefix = 'SID:'	# prefix for key in memory cache 
 	__mc_ttl = 2 * 60 * 60	# keep session data in memory cache for 2 hours

 	def __init__(self):
 		pass

 	@classmethod
 	def get_new_session_id(cls, user_data, request=None):

 		tc = time.time()
 		obj = {
 			'ip': util.get_client_ip(request),
 			'ua': util.get_client_user_agent(request),
 			'tc': tc,
 			'user_data': user_data
 		} 
 		str_obj = json.dumps(obj)
 		session_id = '%s.%s' % (hashlib.md5(str_obj).hexdigest(), str(tc))
 		key = cls.__mc_prefix + session_id

 		# write into memory cache
 		mc = MemCache()
		mc.set(key, str_obj, ttl=cls.__mc_ttl)
		rs = mc.get(key)
 		# TODO: may need writing into DB for record

 		return session_id if rs else None

 	@classmethod
 	def get_session_object(cls, session_id):
 		# TODO: may need to verify using user_agent hash
 		key = cls.__mc_prefix + session_id
 		mc = MemCache()
 		rs = mc.get(key)
 		return rs


if __name__ == "__main__":
	sid = SessionID.get_new_session_id({'user':'admin', 'pass':'0000'})
	print 'sid:%s is_valid:%s' % (sid, SessionID.is_session_valid(sid))



