#!/usr/bin/env python
"""
Poll the OVS state every <period> time
Usage: python ovs_state_self_polling.py -i 10.1.0.12 -p 10 
"""

__AUTHOR__ = 'yongxiang'
__VERSION__ = '1.0'
__DATE__ = '2015/06/12'


import os
import sys
import json
import time
import datetime
from optparse import OptionParser

def ovs_state_poll(ip, outfile, period):
        while True:
                if outfile == "sys.stdout":
                        fo = sys.stdout
                else:
                        fo = open(outfile, 'a') # option 'a' for multiple calls
                state_dump = dict()
		state_dump['IP'] = ip
                state_dump['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%3d') # addtional timestamp 
#                content = os.popen('ovsdb-client dump -f json --detach').read() # run as daemon
		content = os.popen('ovsdb-client dump -f json').read()
	      	for line in content.strip('\n').split('\n'):
                        table = json.loads(line)
                        state_dump[table['caption']] = table # tablename is table['caption']

                print >> fo, json.dumps(state_dump, sort_keys=True) + "," # without indent
                
                if outfile != "sys.stdout": # don't close stdout
                        fo.close()
                
                ## sleep for a while
                time.sleep(float(period)) 


def main():
        parser = OptionParser('usage: %prog')
	parser.add_option('-i', '--ip', metavar='ip', default='127.0.0.1', help='node IP address')
        parser.add_option('-o', '--outfile', metavar='outfile', default='sys.stdout', help='output json file')
        parser.add_option('-p', '--period', metavar='period', help='polling period')
        (options, args) = parser.parse_args()
        ovs_state_poll(options.ip, options.outfile, options.period)

if __name__ == '__main__':
        main()

