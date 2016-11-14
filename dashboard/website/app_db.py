
_author = 'ali.mazouchi'

import json
import hashlib
import psycopg2
import base64

from settings import settings


class AppDB(object):
 	"""
 		Application DataBase
 		Provide connection to database and authenticate based on user

 		User Table:
 			CREATE TABLE users (id serial, user_name varchar(50), pass text, salt text, data_obj text);
 			data_obj is a string form of json to keep user's customer_id, first_name, last_name and more 
	"""

	__database = settings('AppDB__database')	# database for webApp
	__user = settings('AppDB__user') 			# username for authebtication of database 
	__table_users = settings('AppDB__table_users')	# accounts information

	__conn = None			# connection to PostgreSQL


	def __init__(self, data_obj, conn=None):
 		self.__data_obj = data_obj
 		self.__conn = conn


	@classmethod
	def __dbconn(cls):
		'''
			Establish connection to DataBase
		'''
		conn1 = cls.__conn
		if not conn1:
			try:
				conn1 = psycopg2.connect(database=cls.__database, user=cls.__user) 
				cur = conn1.cursor()
				cur.execute('SELECT version()')
				print 'Connected to DB:%s' % cur.fetchone()
				cls.__conn = conn1
			except psycopg2.DatabaseError, e:
				print 'AppDB.__dbconn, Error %s' % e
		return cls.__conn


	@classmethod
	def __find_user(cls, username):
		'''
			Find record for username, if valid return the record as a dictionary otherwise return None
		'''
		rs = {}
		try:
			cur = cls.__conn.cursor()
			ex1 = cur.execute("SELECT * FROM %s WHERE user_name='%s'" % (cls.__table_users, username))
			xid, un, password, salt, data_obj = cur.fetchone()
			if un and data_obj:
				data_obj = json.loads(base64.b64decode(data_obj))
				data_obj['user_name'] = un
				rs = {'user_name':un, 'password': password, 'salt': salt, 'data_obj': data_obj}
				return rs
		except Exception as e:
			# print 'AppDB.__find_user, Error %s' % repr(e)
			rs['err'] = repr(e)
		return rs


	@classmethod
	def create_new_user(cls, username, password, data_obj):
		'''
			Create a new user account and return dictionary
			success: returns key db  with value for user AppDB
			error: value of key err for error message
		'''
		conn = cls.__dbconn()
		rs = {'user_name': username}
		if conn:
			try:
				# removing invalid chars to protect from sql injection
				invalid_chars = [' ', ',', ';', '(', ')', '*', '#', '=']
				username2 = username.encode('ascii', 'ignore').translate(None, ''.join(invalid_chars))
				if username != username2:
					rs['err'] = 'username includes invalid charachters.'
					return rs

				user_data = cls.__find_user(username)
				if user_data:
					if user_data.get('err'):
						rs['err'] = user_data.get('err')
					else:
						rs['err'] = 'username already exists.'
				else:
					cur = conn.cursor()
					if not data_obj:
						data_obj = {}
					# TODO: replace it with crypto
					salt = hashlib.md5(username + 'abc').hexdigest()
					pass_hash = hashlib.sha224(password + salt).hexdigest()

					data_obj_encoded = base64.b64encode(json.dumps(data_obj)) 	# protect from sql injection

					cur.execute("INSERT INTO %s (user_name, pass, salt, data_obj) VALUES ('%s', '%s', '%s', '%s')" % (cls.__table_users, username, pass_hash, salt, data_obj_encoded))
					conn.commit()
					rs['db'] = cls.db(username, password)

			except psycopg2.DatabaseError, e:
				conn.rollback()
				print 'AppDB.create_new_user, Error %s' % e
				rs['err'] = repr(e)
		return rs


	@classmethod
	def authenticate_user(cls, conn, username, password):
		'''
			Find user and authenticate the password, if valid return user data object
		'''
		data = cls.__find_user(username)
		if data:
			data_obj = data['data_obj']
			pass_hash = data['password']
			# TODO: replace it with crypto
			if  data['password'] == hashlib.sha224(password + data['salt']).hexdigest():
				return data_obj
		return None


	@classmethod
	def db(cls, username, password):
		'''
			Authenticate the user 
			success: provide user AppDB
			error: None
		'''
		conn = cls.__dbconn()
		if conn:
			try:
				data_obj = cls.authenticate_user(conn, username, password)
				if data_obj:
					return AppDB(data_obj, conn)

			except Exception as e:
				print 'AppDB.db, Error %s' % repr(e)
		return None


	def user_data(self):
		return self.__data_obj


	@classmethod
	def process(cls, obj):
		'''
			processing obj (json) passed through apis, keys may be required:
			username: username for inquiery or authentication or creating acccount
			password: password for authentication or creating acccount
			create:1  flag to create a new account
			in case of error, key 'err' exists in response
		'''
		rs = {}
		# authenticate
		if obj:
			username = obj.get('username')
			password = obj.get('password')

			# data object for extra data to be keept
			data_obj = obj.copy()
			for k in ['username', 'password', 'act']:
				if k in data_obj:
					del data_obj[k]

			print 'process obj:', repr(obj)
			rs['username'] = username
			if obj.get('act') == 'create':				# creating new account, needs customer_id
				if username and password:
					if not data_obj.get('customer_id'):
						rs['err'] = 'customer_id is required to create account.'
					else:
						rs = cls.create_new_user(username, password, data_obj)
						db = rs.get('db')
						if db:
							rs = db.user_data()

			elif username and password:
				db = cls.db(username, password)
				if db:
					rs = db.user_data()
				else:
					rs['err'] = 'Not valid username or password'

		return rs


if __name__ == "__main__":
	test_list = [
		{'username': 'ali5', 'password': 'xabc'},
		{'username': 'ali6', 'password': 'xabc', 'customer_id':'st2', 'act':'create'},
		{'username': 'ali6', 'password': '123', 'customer_id':'st2', 'act':'create'},
		{'username': 'ali7=', 'password': '123', 'customer_id':'st2', 'act':'create'},
		{'username': 'ali7=', 'password': '123'}

	]
	for q in test_list:
		print 'query: %s' % q
		rs = AppDB.process(q)
		print 'result: %s \n\n' % repr(rs)


