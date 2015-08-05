#!/usr/bin/env python

'''
Recursively process log files in the directory: 
1) compact multi-line log into single-line, and 
2) extract log with timestamp in [low, high) range
3) convert the timestamp into new timezone
Usage: python compact_extract_convert_timezone_log.py -d logdir -l low_timestamp -h high_timestamp
'''
import os
import re
import pytz, datetime
from optparse import OptionParser

def convert_timezone(timestamp, fromzone, tozone):
        format = "%Y-%m-%d %H:%M:%S.%f"
        local = pytz.timezone(fromzone)
        remote = pytz.timezone(tozone)
        naive = datetime.datetime.strptime(timestamp, format)
        local_dt = local.localize(naive, is_dst=None)
        remote_dt = local_dt.astimezone(remote)
        return remote_dt.strftime(format)[0:-3] # take 3 out 6 digits of the milisecond 


def compact_extract(oldlog, newlog, low, high, fromzone, tozone):
	with open(oldlog) as fo:
                lines = fo.read().splitlines()#strip '\n'
                fo.close()
	with open(newlog, 'w') as fn:
		pattern = r'^\d{4}-\d{2}-\d{2}' # date pattern
                prog = re.compile(pattern)
		noskip = False 
		# compact multi-line log into single-line by timestamp
		for line in lines:
			if prog.match(line):
				if line >= low and line < high: # extract line within [low, high) timestamp
					#timestamp = line[:23]# 2015-05-30 22:54:13.926 
					line = convert_timezone(line[:23], fromzone, tozone) + line[23:]
					fn.write('\n' + line) # start a newline
					noskip = True # keep the following non-date lines 
			elif noskip:
				fn.write(' ' + line) # append
			# else: pass		
		fn.close()

def run(logdir, low, high, fromzone, tozone):
	for root, dirs, files in os.walk(logdir):
		for file in files:
			oldlog = os.path.join(root, file)
			newlog = os.path.join(root, 'new_' + file)
			print 'old: ' + oldlog 
			print 'new: ' + newlog
			compact_extract(oldlog, newlog, low, high, fromzone, tozone)
		for dir in dirs:
			run(dir, low, high, fromzone, tozone) # recursively

def main():
        parser = OptionParser('usage: %prog')
	parser.add_option('-d', '--logdir', metavar='logdir')
        parser.add_option('-l', '--low', metavar='low')
        parser.add_option('-u', '--high', metavar='high')
	parser.add_option('-f', '--fromzone', metavar='fromzone', default='US/Pacific')
	parser.add_option('-t', '--tozone', metavar='tozone', default='UTC')
        (options, args) = parser.parse_args()
	run(options.logdir, options.low, options.high, options.fromzone, options.tozone)
	
if __name__ == '__main__':
        main()

