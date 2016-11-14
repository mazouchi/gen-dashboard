
_author = 'ali.mazouchi'


def settings(name):
	global __settings
	return __settings.get(name)

__settings = {
	'AppDB__database': 'udash',			# database for webApp
	'AppDB__user': 'amazouchi', 		# username for authebtication of database
	'AppDB__table_users': 'users',		# accounts information

	'redis__host': 'localhost',
	'redis__port': 6379

}
