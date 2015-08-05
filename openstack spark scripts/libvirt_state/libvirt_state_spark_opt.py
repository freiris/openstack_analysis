"""
Remove successive/adjacent duplicates in libvirt Virtual Machine states
"""

from __future__ import print_function
import sys
import json
from pyspark import SparkContext, SparkConf

## ad-hoc
#referTimestamp = '2015-06-16 09:42:03' # timestamp of state should later than that of operation

def unique(VMStates):
        uniqVMStates = []
        referState = VMStates[0]
        for state in VMStates[1:]: # we must record the first occurance of a new state, not the last. (similar to the upper-jump)
             for key in referState:
                     if key != "timestamp":
                             if referState[key] != state[key]:
                                     uniqVMStates.append(referState)
                                     referState = state
                                     break
        uniqVMStates.append(referState)
        return uniqVMStates



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: libvirt_state_spark_opt.py <pathIn> <pathOut>")
        exit(-1)

    conf = SparkConf()
    conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    conf.set("spark.speculation", "true")
    conf.setAppName("PythonLibvirtState")
    sc = SparkContext(conf=conf)

    pathIn = sys.argv[1]
    pathOut = sys.argv[2] 

    print('pathIn = %s, pathOut = %s' % (pathIn, pathOut))

    libvirtStates = sc.textFile(pathIn)
    libvirtParsedRDD = (libvirtStates
			.map(lambda line: json.loads(line.strip(',\n'))))
#            		.cache())

# reduceByKey leads to many retrials, and finally aborted. why?
#    libvirtReduceRDD = (libvirtParsedRDD
#            		.map(lambda vmState: (vmState["uuid"], [vmState]))
#            		.reduceByKey(lambda p, q: p + q))

    libvirtReduceRDD = (libvirtParsedRDD
#			.filter(lambda vmState: vmState['timestamp'] >= referTimestamp) # ad-hoc
			.map(lambda vmState: (vmState["uuid"], vmState))
			.groupByKey())

    libvirtReduceSortedRDD = (libvirtReduceRDD
			      .mapValues(lambda vms: sorted(vms, key = (lambda vm: vm["timestamp"]), reverse = False)))


    libvirtReduceSortedDiffRDD = (libvirtReduceSortedRDD
				  .mapValues(lambda vms: unique(vms)))

#    libvirtReduceSortedDiffRDD.map(lambda x: json.dumps(x)).saveAsTextFile(pathOut) # dump to json format, then save as textfile
    libvirtReduceSortedDiffRDD.saveAsTextFile(pathOut) 

    sc.stop()
