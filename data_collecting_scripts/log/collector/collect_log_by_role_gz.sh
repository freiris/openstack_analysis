#!/bin/sh
## collect log files based on node role

# $1: username
# $2: IP file
# $3: role (compute, network, controller)
# $4: #latest-files to include (*.log, *.log-xxx.gz(s))

for i in `cat $2`;do
                echo $i
                n=`echo $i | cut -d "." -f 4 | awk '{printf("%03d", $1)}'` # 3 digits with leading 0 for padding
                mkdir -p ./log-$n

		case $3 in
			###############compute node################### 
			"compute") # compute node
			echo "compute node"
			mkdir -p ./log-$n/neutron
			mkdir -p ./log-$n/nova
			neutron_log="/var/log/neutron/openvswitch-agent.log"
			for f1 in `ssh $1@$i "ls -t $neutron_log* | head -n $4"`; do # *.log and latest *.log-xxx.gz
                        	rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/neutron
			done

			nova_log="/var/log/nova/compute.log"	
			for f1 in `ssh $1@$i "ls -t $nova_log* | head -n $4"`; do # *.log and latest *.log-xxx.gz
                                rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/nova
                        done
			;;
			##################network node####################
			"network") # network node
			echo "network node"
			mkdir -p ./log-$n/neutron
			neutron_logs=("/var/log/neutron/dhcp-agent.log" "/var/log/neutron/l3-agent.log"\
			 	"/var/log/neutron/metadata-agent.log" "/var/log/neutron/openvswitch-agent.log")
			for f in "${neutron_logs[@]}"; do
				for f1 in `ssh $1@$i "ls -t $f* | head -n $4"`; do # *.log and latest *.log-xxx.gz
					rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/neutron
				done
			done
			;;
			################controller node####################
			"controller") # controller node
			echo "controller node"
			mkdir -p ./log-$n/cinder
			mkdir -p ./log-$n/glance
			mkdir -p ./log-$n/keystone
			mkdir -p ./log-$n/neutron
			mkdir -p ./log-$n/nova
			
			# cinder (replaced by Ceph)
			cinder_logs=("/var/log/cinder/api.log" "/var/log/cinder/cinder.log"\
				"/var/log/cinder/scheduler.log"  "/var/log/cinder/volume.log")
			for f in "${cinder_logs[@]}"; do
                                for f1 in `ssh $1@$i "sudo sh -c 'ls -t $f*' | head -n $4"`; do # sudo sh -c 'ls -t $f*' to enable wildcard (*)
                                        rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/cinder
                                done
                        done

			# glance
			glance_logs=("/var/log/glance/api.log" "/var/log/glance/image-cache.log" "/var/log/glance/registry.log")
			for f in "${glance_logs[@]}"; do
                                for f1 in `ssh $1@$i "sudo sh -c 'ls -t $f*' | head -n $4"`; do  
                                        rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/glance
                                done
                        done

			# keystone
			keystone_log="/var/log/keystone/keystone.log"
                        for f1 in `ssh $1@$i "sudo sh -c 'ls -t $keystone_log*' | head -n $4"`; do
                                rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/keystone
                        done			

			# neutron
			neutron_log="/var/log/neutron/server.log"
                        for f1 in `ssh $1@$i "sudo sh -c 'ls -t $neutron_log*' | head -n $4"`; do
                                rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/neutron
                        done

			# nova
			nova_logs=("/var/log/nova/api.log" "/var/log/nova/cert.log" "/var/log/nova/conductor.log"\
				"/var/log/nova/consoleauth.log" "/var/log/nova/metadata-api.log"\
				"/var/log/nova/nova-manage.log" "/var/log/nova/scheduler.log" )
			for f in "${nova_logs[@]}"; do
                                for f1 in `ssh $1@$i "sudo sh -c 'ls -t $f*' | head -n $4"`; do  
                                        rsync -a -e "ssh" --rsync-path="sudo rsync" $1@$i:$f1 ./log-$n/nova
                                done
                        done
			;;
			*)
			echo "$1 is unknown"
			;;
		esac
done

# unzip the *.gz 
find ./ -type f -name "*.gz" | xargs gunzip

echo "COMPLETE"
