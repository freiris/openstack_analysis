#!/usr/bin/env python
"""
Collect the domain (virtual machine) state information on each node (physical machine) from libvirt

Usage:
	$ python libvirt_domain_state.py -u user -i ip.txt  -o domain_state.json
"""

import sys
import json
import libvirt
import xmltodict
import datetime
import time
from optparse import OptionParser


__AUTHOR__ = 'yongxiang'
__VERSION__ = '1.2'
__DATE__ = '2015/06/06'

# states enumration
states = {
    libvirt.VIR_DOMAIN_NOSTATE: 'nostate',
    libvirt.VIR_DOMAIN_RUNNING: 'running',
    libvirt.VIR_DOMAIN_BLOCKED: 'blocked', # blocked on resource
    libvirt.VIR_DOMAIN_PAUSED: 'paused', # paused by user
    libvirt.VIR_DOMAIN_SHUTDOWN: 'shutdown', # being shut down
    libvirt.VIR_DOMAIN_SHUTOFF: 'shutoff',
    libvirt.VIR_DOMAIN_CRASHED: 'crashed',
}

def domain_state_poll(user, IP, outfile, period):
	while True:
		if outfile == "sys.stdout":
			fo = sys.stdout
        	else:
                	fo = open(outfile, 'a') # option 'a' for multiple calls
	#       uri = 'qemu+ssh://' + user + '@' + IP + '/system'
	       	uri = 'qemu+tcp://' + user + '@' + IP + '/system'
	#	conn = libvirt.openReadOnly(uri) # can't get all information
	        conn = libvirt.open(uri) # doesn't work on production cluster with qemu+ssh
		
		print 'succeed to OPEN connection: %s' % uri

		domain = dict()
		domain['nodeIP'] = IP
	        domain['node'] = conn.getHostname()
	        for dom in conn.listAllDomains(flags=(1|2)): # 1: active, 2: inactive
	               	#domain['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3d') # addtional timestamp 	
			domain['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%3d')
			domain['name'] = dom.name() # only unique within the libvirt on a node
	                domain['uuid'] = dom.UUIDString() # global unique
	                domain['state'] = states[dom.info()[0]] # state is 0~7, map to string description
	                domain['isActive'] = dom.isActive() # active or inactive        
		#	domain['xmldesc'] = xmltodict.parse(dom.XMLDesc(flags=(1|2))) # configuration information of the domain 	
	                xmldict = xmltodict.parse(dom.XMLDesc(flags=(1|2))) # selected device configuration of the domain
			devices = set(['console', 'disk', 'interface', 'serial']).intersection(xmldict['domain']['devices'].keys())# interface is not common
			domain['devices'] = dict()
			for device in devices:
				domain['devices'][device] = xmldict['domain']['devices'][device]
	
		#	print >> fo, json.dumps(domain, sort_keys=True, indent=4) + ","
			print >> fo, json.dumps(domain, sort_keys=True) + "," # without indent
	
		conn.close()
	       	print 'succeed to CLOSE connection to %s' % uri
		
		if outfile != "sys.stdout": # don't close stdout
               		fo.close()
		
		## sleep for a while
		time.sleep(float(period))

       		"""
		## more information to extract from libvirt
        	print conn.listAllDomains(flags=1)
        	print conn.listAllDevices(flags=1)
        	print conn.listAllInterfaces(flags=1)
        	print conn.listAllNWFilters(flags=1)
        	print conn.listAllNetworks(flags=1)
        	print conn.listAllSecrets(flags=1)
        	print conn.listAllStoragePools(flags=1)
        	"""
	# stop/terminate by external operation
	


def main():
        parser = OptionParser('usage: %prog')
	parser.add_option('-u', '--user', metavar='user', help='user in local node')	
        parser.add_option('-i', '--ip', metavar='ip', help='IP of local node')
        parser.add_option('-o', '--outfile', metavar='outfile', default='sys.stdout', help='output json file')
	parser.add_option('-p', '--period', metavar='period', help='polling period')
        (options, args) = parser.parse_args()
       	domain_state_poll(options.user, options.ip, options.outfile, options.period)

if __name__ == '__main__':
	main()
