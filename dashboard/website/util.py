
_author = 'ali.mazouchi'


import logging
import datetime
import boto3

__logger = None

def _logger():
	global __logger
	if not __logger:
		logger = logging.getLogger('genapsys-webapp')
		fh = logging.FileHandler('webapp.log')
		# fh.setLevel(logging.DEBUG)
		logger.addHandler(fh)
		__logger = logger
	return __logger


# set cookie in response
def set_cookie(response, key, value, expire_in_sec):
  if expire_in_sec is None:
    expire_in_sec = 30 * 60  # 30 mins
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=expire_in_sec), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=expire_in_sec, expires=expires, domain=None, secure=False)


def get_cookie(request, key):
	return request.COOKIES.get(key) 


def get_client_ip(request):
	if not request:
		return ''
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip


def get_client_user_agent(request):
	return request.META['HTTP_USER_AGENT'] if request else ''


# ================   S3 Download & Upload

def download_file_url(user_obj):
	'''
		credentials must be in ~/.aws
			- aws_access_key_id="XXX"
			- aws_secret_access_key="XXX"
		bucket_name & key name in settings
	'''
	s3 = boto3.client('s3')
	#s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
	# Generate the URL to get 'key-name' from 'bucket-name'
	url = s3.generate_presigned_url(
	    ClientMethod='get_object',
	    Params={
	        'Bucket': 'bucket-name',
	        'Key': 'key-name'
	    },
	    ExpiresIn=3600
	)
	return url


def upload_file_post(user_obj):
	s3 = boto3.client('s3')
	post = s3.generate_presigned_post(
	    Params={
	        'Bucket': 'bucket-name',
	        'Key': 'key-name'
	    },
	    ExpiresIn=3600
	)
	return post

	# # Use the returned values to POST an object. Note that you need to use ALL
	# # of the returned fields in your post. You can use any method you like to
	# # send the POST, but we will use requests here to keep things simple.
	# files = {"file": "file_content"}
	# response = requests.post(post["url"], data=post["fields"], files=files)

def s3_file_process(data_obj):
	pass
