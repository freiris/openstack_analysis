#!/usr/bin/env python
"""
Create a trace table for the database in default tracedb.
Create an after_[insert, update, delete] trigger for each table, and a disable_switch for each trigger (limited in the same session). 
Trace the NEW.* for insert and update, the OLD.* for delete.
We keep the NULL value, and use semicolon(;) as delimiter.

NOTE: 
trigger_name = table + '_' + trigger_time + '_' + trigger_event + '_trigger', i.e. quotas_AFTER_UPDATE_trigger
trigger_disable = db + '_' + table + '_' + trigger_time + '_' + trigger_event + '_disable', i.e. nova_quotas_AFTER_UPDATE_disable
"""
import MySQLdb
from optparse import OptionParser


__AUTHOR__ = 'shuhao+yong'
__VERSION__ = '1.2'
__DATE__ = '2015/01/11'



def _run(host, port, db, user, password, tracedb):
	connection = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=db)
 	cursor = connection.cursor()
	
	# create an trace table for the database
	#tracedb = db # if we set to db, we get an in-place version
	trace_table = db + '_trace'
	create_trace_table  = "CREATE TABLE IF NOT EXISTS `%(tracedb)s`.`%(trace_table)s`\
			(id INT AUTO_INCREMENT PRIMARY KEY, timestamp TIMESTAMP, event VARCHAR(16), tablename VARCHAR(32), content VARCHAR(1024))"\
			 %{'tracedb' : tracedb, 'trace_table' : trace_table} # avoid reserved word conflict by left single quote (``)
	cursor.execute(create_trace_table)

	# get tables in the database
	cursor.execute('USE %s' % (db))
	cursor.execute('show tables') # or select from information_schema.tables
        tables = cursor.fetchall()

	# create after_[insert, update, delete] trigger for each table
	for item in tables:
		table = item[0]
		# get concatenated column names with prefix
		cols_dict = dict()
		for prefix in ['NEW.', 'OLD.']:
			get_cols = "SELECT GROUP_CONCAT(CONCAT('%(prefix)s', COLUMN_NAME) separator ', ')\
				FROM information_schema.COLUMNS \
				WHERE TABLE_SCHEMA = '%(db)s' \
				AND TABLE_NAME = '%(table)s'" \
				%{'prefix': prefix, 'db': db, 'table': table}
			cursor.execute(get_cols)
			res = cursor.fetchall()
			cols_dict[prefix] = res[0][0]
	
		# create after event trigger, thus we can guarantee the transaction has completed
		trigger_time = 'AFTER'	
		for trigger_event in ['INSERT', 'UPDATE', 'DELETE']:
			if trigger_event == 'DELETE':
				cols = cols_dict['OLD.'] # trace the OLD value for DELETE operation. Required to determine the death of a row. 
			else:
				cols = cols_dict['NEW.']
			# keep 'NULL' value in the field, don't ignore when concat_ws()
			cols = ', '.join(map(lambda f: "IFNULL(%s, 'NULL')"%f, cols.split(', '))) # if the value is null, set as empty string
			

			trigger_name = table + '_' + trigger_time + '_' + trigger_event + '_trigger'# unique within database is OK 
			trigger_disable = db + '_' + table + '_' + trigger_time + '_' + trigger_event + '_disable' # global variable 
			# drop trigger with the same name
			cursor.execute('DROP TRIGGER IF EXISTS %s' % (trigger_name))

			# create trigger
			create_trigger = "CREATE TRIGGER %(trigger_name)s %(trigger_time)s %(trigger_event)s ON `%(table)s`\
					FOR EACH ROW \
					BEGIN \
						IF @%(trigger_disable)s IS NULL THEN \
							INSERT INTO `%(tracedb)s`.`%(trace_table)s` \
							SELECT NULL, NOW(), '%(trigger_event)s', '%(db)s.%(table)s', CONCAT_WS(';', %(cols)s)\
							FROM `%(table)s`\
							LIMIT  1;\
						END IF;\
					END;"\
					%{'trigger_name': trigger_name, 'trigger_time': trigger_time, 'trigger_event': trigger_event,\
					'trigger_disable': trigger_disable, 'db': db, 'table': table, 'tracedb': tracedb, 'trace_table': trace_table,\
					'cols': cols} 
					 #we avoid WHERE clause with LIMIT 1
			print create_trigger
			cursor.execute(create_trigger)
def main():
	parser = OptionParser('usage: %prog')
    	parser.add_option('', '--host', metavar='host', default='localhost', help='mysql host address, default: %default')
    	parser.add_option('', '--port', metavar='port', default=3306, type='int', help='mysql port, default: %default')
	parser.add_option('', '--db', metavar='db', default='mysql', help='database, default: %default')
    	parser.add_option('', '--user', metavar='user', default='root', help='mysql user, default: %default')
    	parser.add_option('', '--password', metavar='password', default='root', help='mysql password, default: %default')
   	parser.add_option('', '--tracedb', metavar='tracedb', default='tracedb', help='trace database, default: %default')
	(options, args) = parser.parse_args()
    	_run(options.host, options.port, options.db, options.user, options.password, options.tracedb)
 
if __name__ == '__main__':
    main()
