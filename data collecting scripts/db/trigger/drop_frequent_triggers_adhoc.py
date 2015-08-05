#!/usr/bin/env python
"""
Drop the frequently updating triggers
"""
import MySQLdb
from optparse import OptionParser


__AUTHOR__ = 'shuhao+yong'
__VERSION__ = '1.0'
__DATE__ = '2015/05/24'

triggers = ['nova.services_AFTER_UPDATE_trigger',
	'nova.compute_nodes_AFTER_UPDATE_trigger',
	'cinder.services_AFTER_UPDATE_trigger', 
	'neutron.agents_AFTER_UPDATE_trigger', 
	'neutron.ports_AFTER_UPDATE_trigger']









def _run(host, port, db, user, password):
	connection = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=db)
 	cursor = connection.cursor()
	# drop trigger
	for trigger in triggers:
		drop_trigger = "DROP TRIGGER IF EXISTS " + trigger
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
