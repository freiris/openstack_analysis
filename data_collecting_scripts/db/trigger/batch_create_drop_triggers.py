#!/usr/bin/env python
'''
create/drop triggers for cinder, glance, keystone, neutron, nova in batch
'''



import create_triggers
import drop_triggers
from optparse import OptionParser

tracedb = 'tracedb'
dbs = ['cinder', 'glance', 'keystone', 'neutron', 'nova']

def batch_create_drop(host, port, user, password, action):
	if action == 'create':
		for db in dbs:
			create_triggers._run(host, port, db, user, password, tracedb)
	elif action == 'drop':
		for db in dbs:
			drop_triggers._run(host, port, db, user, password)
	else:
		print action + 'is not supported'

def main():
        parser = OptionParser('usage: %prog')
        parser.add_option('', '--host', metavar='host', default='localhost', help='mysql host address, default: %default')
        parser.add_option('', '--port', metavar='port', default=3306, type='int', help='mysql port, default: %default')
        parser.add_option('', '--user', metavar='user', default='root', help='mysql user, default: %default')
        parser.add_option('', '--password', metavar='password', default='root', help='mysql password, default: %default')
        parser.add_option('', '--action', metavar='action', default='create', help='create or drop, default: %default')
        (options, args) = parser.parse_args()
        batch_create_drop(options.host, options.port, options.user, options.password, options.action)

if __name__ == '__main__':
    main()

