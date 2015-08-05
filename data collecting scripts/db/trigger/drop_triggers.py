#!/usr/bin/env python
"""
Drop all triggers in the database
"""
import MySQLdb
from optparse import OptionParser


__AUTHOR__ = 'shuhao+yong'
__VERSION__ = '1.0'
__DATE__ = '2015/03/08'



def _run(host, port, db, user, password):
	connection = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=db)
 	cursor = connection.cursor()
	# get trigger names from information_schema
	get_triggers = "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS\
			WHERE TRIGGER_SCHEMA = '%(db)s'" % {'db': db}
	print get_triggers
	cursor.execute(get_triggers)
	triggers = cursor.fetchall()
	# drop trigger
	for item in triggers:
		trigger = item[0]
		drop_trigger = "DROP TRIGGER IF EXISTS %(db).s%(trigger)s" % {'db': db, 'trigger': trigger}
		print drop_trigger
		cursor.execute(drop_trigger)
	
	
		
def main():
	parser = OptionParser('usage: %prog')
    	parser.add_option('', '--host', metavar='host', default='localhost', help='mysql host address, default: %default')
    	parser.add_option('', '--port', metavar='port', default=3306, type='int', help='mysql port, default: %default')
	parser.add_option('', '--db', metavar='db', default='mysql', help='database, default: %default')
    	parser.add_option('', '--user', metavar='user', default='root', help='mysql user, default: %default')
    	parser.add_option('', '--password', metavar='password', default='root', help='mysql password, default: %default')
   	(options, args) = parser.parse_args()
    	_run(options.host, options.port, options.db, options.user, options.password)
 
if __name__ == '__main__':
    main()
