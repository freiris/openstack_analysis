#!/usr/bin/env python
'''
rabbitmq message trace parser

usage:
	$ python parse_recursive_deep_2.py --infile input.json --outfile output.json
'''

import json
import sys
from pprint import pprint
from optparse import OptionParser


__AUTHOR__ = 'yongxiang'
__VERSION__ = '1.3'

def _recursive_parse(data):
	if isinstance(data, dict): # dictionary
		for key, value in data.items():
			data[key] = _recursive_parse(value)
		return data
	elif isinstance(data, list): # list
		for i in range(len(data)):
			data[i] = _recursive_parse(data[i])
		return data
	elif isinstance(data, unicode) or isinstance(data, str): # unicode/string
		try: # test whether a JSON string or not
			new_data = json.loads(data)# new_data can be dict, list, unicode...
		except: # ordinary string, not in JSON format
			return data
		else: # valid JSON string
			return _recursive_parse(new_data)
	else: # other primary types, i.e. int,long,float,True, False, None 
		return data

def _msgparse(infile, outfile):
        json_in = open(infile)
#        json_data = json.load(json_in)#load input
        if outfile == "sys.stdout":
                json_out = sys.stdout
        else:
                json_out = open(outfile, 'w')
        for line in json_in:
		item = line.strip(',\n')
                new_item = _recursive_parse(item)
#		print >> json_out, json.dumps(new_item, sort_keys=True) + "," #single line without indent
		print >> json_out, json.dumps(new_item, sort_keys=True, indent=4) + "," # indent with 4 space
        json_in.close()
        json_out.close()


def main():
        parser = OptionParser('usage: %prog')
        parser.add_option('-i', '--infile', metavar='infile', help='input json file')
        parser.add_option('-o', '--outfile', metavar='outfile', default='sys.stdout', help='output json file')
        (options, args) = parser.parse_args()
        _msgparse(options.infile, options.outfile)

if __name__ == '__main__':
	main()
