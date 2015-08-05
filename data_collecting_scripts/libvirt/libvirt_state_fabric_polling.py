from fabric import tasks,state
from fabric.api import *
import sys
import time

ipfile="/root/libvirt_state/ip_n250.txt" # fabric local machine
env.hosts=[line.strip('\n') for line in open(ipfile)]
print env.hosts
time.sleep(2)

script_dir = '/home/yong/libvirt_state/scripts'
output_dir = '/home/yong/libvirt_state/libvirt_state_0714'
period = sys.argv[1] # polling period


@parallel
def worker():
	with settings(user='yong', use_sudo=True):
		ip = env.host	
		batch_polling = 'python  %(script_dir)s/libvirt_state_self_polling.py -u yong -i %(ip)s -o %(output_dir)s/%(ip)s.out -p %(period)s' % \
                {'script_dir': script_dir, 'ip': ip, 'output_dir': output_dir, 'period': period}
		print batch_polling 
		run(batch_polling)

		#detach_batch_polling = 'dtach -n `%s`' % batch_polling
		#print detach_batch_polling  	
		#run(detach_batch_polling)

def main():
#    print state.output
    tasks.execute(worker)

if __name__ == '__main__':
    main()
