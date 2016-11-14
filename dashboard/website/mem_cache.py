
_author = 'ali.mazouchi'


import json
import redis

from settings import settings

class MemCache(object):
	"""
		Memory Cache for web applicationm, wrapper for redis
	"""
	__host = settings('redis__host')
	__port = settings('redis__port')
	__JSON_OBJECT = '[-OBJ-]'	# indicator for json object format

	def __init__(self, settings=None):
		self._host = None
		self._port = None
		self._conn = self.conn(settings)

	def conn(self, settings):
		if settings:
			# TODO: get host and port info from settings
			pass
		else:
			self._host = self.__host
			self._port = self.__port
		r = redis.StrictRedis(host=self._host, port=self._port, db=0)
		return r

	@classmethod
	def json2objstring(cls, json_obj):
		'''
			converting json object to a string with prefix [-OBJ-]
		'''
		rs = json_obj
		if isinstance(json_obj, (dict, list)):
			rs = cls.__JSON_OBJECT + json.dumps(json_obj)
		return rs

	@classmethod
	def objstring2json(cls, objstring):
		'''
			converting object string with prefix [-OBJ-] to json object
			if input is not a velid object string returns original input
		'''
		rs = objstring
		len_flag = len(cls.__JSON_OBJECT)
		if objstring and objstring[0:len_flag] == cls.__JSON_OBJECT:
			rs = json.loads(objstring[len_flag:])
		return rs

	def set(self, key, value, namespace=None, ttl=None):
		'''
			set key-value into memory cache
			namespace: same as hash name, if namespace presents key-value is added to namespace
			ttl: time to expire
		'''
		rs = None
		value = self.json2objstring(value)
		if namespace:
			rs = self._conn.hset(namespace, key, value)
			if ttl != None:
			 	self._conn.expire(namespace, ttl)	# TODO: use pipline
		else:
			rs = self._conn.set(key, value)
			if ttl != None:
			 	self._conn.expire(key, ttl)

		return 1 if rs else 0

	def get(self, key, namespace=None):
		rs = None
		if namespace:
			if key != None:
				v = self._conn.hget(namespace, key)
			else:
				v = self._conn.hgetall(namespace)
		else:
			v = self._conn.get(key)

		if isinstance(v, basestring):
			rs = self.objstring2json(v)
		else:
			rs = v 		# TODO: support json format fot getall
		return rs	

	@classmethod
	def process(cls, obj, prefix='API:'):
		'''
			processing obj (json) passed through apis, keys may be required:
			namespace: namespace for inquirey or setting value
			key: name of the key for inquirey or setting value
			value: for value of the key to be set, value can be string or dictionary ot array 
			in case of error, key 'err' exists in response

			prefix by default 'API:' is added to all namesapces or top level keys
		'''
		rs = {}
		try:
			key = obj.get('key')
			value = obj.get('value')
			namespace = obj.get('namespace')
			ttl = obj.get('ttl', 60*60)
			if namespace:
				namespace = prefix + namespace
			elif key:
				key = prefix + key
			if key:
				mc = MemCache()
				if value:
					rs['rs'] = mc.set(key, value, namespace=namespace, ttl=ttl)
				else:
					rs['value'] = mc.get(key, namespace=namespace)
		except Exception as e:
			rs['err'] = repr(e)

		return rs


if __name__ == "__main__":

	test_list = [
		{'key': 'ali', 'value': 5},
		{'key': 'ali2', 'value': {'a':1, 'b':2}},
		{'key': 'ali'},
		{'namespace': 'test', 'key': 'ali3', 'value': {'a':1, 'b':3}},
		{'namespace': 'test', 'key': 'ali3'},
		{'namespace': 'test', 'key': 'ali4', 'value': {'a':4, 'b':5}},
		{'namespace': 'test'}
	]

	for obj in test_list:
		print 'request obj:', obj
		rs = MemCache.process(obj)
		print 'results rs:%s \n\n' % (rs)


