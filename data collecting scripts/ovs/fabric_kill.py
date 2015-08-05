from fabric import tasks,state
from fabric.api import *
import sys
import time

ipfile="/root/ovs_state/ip_n250_ovs.txt" # fabric local machine
env.hosts=[line.strip('\n') for line in open(ipfile)]
print env.hosts
time.sleep(2)

script_dir = '/home/yong/ovs_state/scripts'
output_dir = '/home/yong/ovs_state/ovs_state_0612'


@parallel
def worker():
	with settings(user='yong', use_sudo=True):
		ip = env.host
		
		batch_kill = "ps aux | grep ovs_state | grep -v grep | awk '{print $2}' | xargs sudo kill -9"
		print batch_kill

		run(batch_kill)

def main():
    print state.output
    tasks.execute(worker)

if __name__ == '__main__':
    main()
