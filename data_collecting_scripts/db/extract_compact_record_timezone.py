#!/usr/bin/env python
"""
Extract records with uuid from tracedb within timestamp [begintime, endtime],
similar to "select into file" procedure. Moreover, compact into single line 

Useage: python extract_compact_record_timezone.py --host 10.1.0.76 --db tracedb --begintime '2015-05-31 05:47:47' --endtime '2015-05-31 08:36:52' 
 
"""
import MySQLdb
import datetime, pytz
from optparse import OptionParser


__AUTHOR__ = 'shuhao+yong'
__VERSION__ = '1.1'
__DATE__ = '2015/06/07'


def extract_by_timestamp_uuid(host, port, db, user, password, begintime, endtime, fromzone, tozone):
	# establish connection to database
	connection = MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=db)
        cursor = connection.cursor()

	# get tables in database
	cursor.execute('USE %s' % (db))
        cursor.execute('show tables') # or select from information_schema.tables
        tables = cursor.fetchall()
	
	# select records within [begintime, endtime] and with uuid into file
	uuid = '.*[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}.*'
	fromtz = pytz.timezone(fromzone)
	totz = pytz.timezone(tozone)
#	fmt = "%Y-%m-%d %H:%M:%S"
	fmt = "%Y-%m-%d %H:%M:%S.%3d"

	for item in tables:
		table = item[0]
		outfile = table + '_uuid.txt'
		fo = open(outfile, 'w')
	
		myextract = "SELECT * FROM %(table)s WHERE timestamp >= '%(begintime)s' and timestamp <= '%(endtime)s'\
			and content REGEXP '%(uuid)s'" % {'table': table, 'begintime': begintime, 'endtime': endtime, 'uuid': uuid}	
		print myextract

		cursor.execute(myextract)
		records = cursor.fetchall()
		for record in records:
			content = record[4].replace('\n', '') # compact the content which may contain '\n' 	 
			timestamp = fromtz.localize(record[1]).astimezone(totz).strftime(fmt)
			print record[1], timestamp

			print >> fo, '%d,"%s","%s","%s","%s"' % (record[0], timestamp, record[2], record[3], content)


def main():
	parser = OptionParser('usage: %prog')
    	parser.add_option('-i', '--host', metavar='host', default='localhost', help='mysql host ip address, default: %default')
    	parser.add_option('-p', '--port', metavar='port', default=3306, type='int', help='mysql port, default: %default')
	parser.add_option('-d', '--db', metavar='db', default='mysql', help='database, default: %default')
    	parser.add_option('-u', '--user', metavar='user', default='root', help='mysql user, default: %default')
    	parser.add_option('-w', '--password', metavar='password', default='root', help='mysql password, default: %default')
   	parser.add_option('-b', '--begintime', metavar='begintime', help='begin time')
	parser.add_option('-e', '--endtime', metavar='endtime', help='end time')
	parser.add_option('-f', '--fromzone', metavar='fromzone', default='US/Pacific', help='from timezone, default: %default')
	parser.add_option('-t', '--tozone', metavar='tozone', default='UTC', help='to timezone, default: %default')
	(options, args) = parser.parse_args()
	extract_by_timestamp_uuid(options.host, options.port, options.db, options.user, options.password,\
	options.begintime, options.endtime, options.fromzone, options.tozone)
 
if __name__ == '__main__':
    main()
