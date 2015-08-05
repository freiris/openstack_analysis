#!/usr/bin/env python
'''
trace messages in the openstack RabbitMQ component
usage: 
1.enable trace_on in the machine where RabbitMQ is 
# rabbitmqctl trace_on  -p /nova  

2.start to trace where this script is
# python tracer-yong-1.4.py --help


'''

import pika
import sys
import json
import datetime
from optparse import OptionParser


__AUTHOR__ = 'ymt+yong'
__VERSION__ = '1.5'
__DATE__ = '2015/08/04'


def _run(host, port, vhost, user, password, rkey, outfile):
	connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port,\
		  	 virtual_host=vhost,credentials=pika.PlainCredentials(user, password)))
	channel = connection.channel()
	result = channel.queue_declare(exclusive=False, auto_delete=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange='amq.rabbitmq.trace', queue=queue_name, routing_key=rkey)
	if outfile == "sys.stdout":
                trace_out = sys.stdout
        else:
                trace_out = open(outfile, 'w') 	

	def callback(ch, method, properties, body):
		ret = {}
		ret["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3d') # keep the milisecond 
		ret["headers"] = properties.headers
		ret["body"] = body
		ret["method"] = {"routing_key": method.routing_key, "delivery_tag": method.delivery_tag,\
				 "consumer_tag":method.consumer_tag, "exchange":method.exchange, "redelivered": method.redelivered}
		#write to stdout or file	
		#print >> trace_out,json.dumps(ret, sort_keys=True, indent=4)+',' # dumps can be easily reloaded as json format
		print >> trace_out,json.dumps(ret, sort_keys=True)+',' # dumps can be easily reloaded as json format	

	channel.basic_consume(callback, queue=queue_name, no_ack=True)
	channel.start_consuming() 
	outfile.close() # close file


def main():
	parser = OptionParser('usage: %prog')
    	parser.add_option('', '--host', metavar='host', default='localhost', help='rabbitmq host address, default: %default')
    	parser.add_option('', '--port', metavar='port', default=5672, type='int', help='rabbitmq port, default: %default')
    	parser.add_option('', '--vhost', metavar='vhost', default='/', help='rabbitmq vhost, default: %default')
    	parser.add_option('', '--user', metavar='user', default='guest', help='rabbitmq user, default: %default')
    	parser.add_option('', '--password', metavar='password', default='guest', help='rabbitmq password, default: %default')
    	parser.add_option('', '--rkey', metavar='rkey', default='#', help='rabbitmq routing key, default: %default')
    	parser.add_option('', '--outfile', metavar='outfile', default='sys.stdout', help='output trace file, default: %default')
   	(options, args) = parser.parse_args()
    	_run(options.host, options.port, options.vhost, options.user, options.password, options.rkey, options.outfile)
 
if __name__ == '__main__':
    main()

