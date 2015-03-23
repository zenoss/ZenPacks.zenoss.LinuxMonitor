##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2008, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


from Products.ZenRRD.CommandParser import CommandParser

class cpu(CommandParser):

    def processResults(self, cmd, result):
        """
        Process the results of "cat /proc/stat".  Take the first line (the cpu
        line) and pick out the values for the various datapoints.
        """

        if cmd.result.output:
            datapointMap = dict([(dp.id, dp) for dp in cmd.points])
        
            # ssCpuSteal does not show up on all systems
            ids = ['ssCpuUser',
                   'ssCpuNice',
                   'ssCpuSystem',
                   'ssCpuIdle',
                   'ssCpuWait',
                   'ssCpuInterrupt',
                   'ssCpuSoftInterrupt',
                   'ssCpuSteal',
                   'ssCpuIdlePerCpu']
            
            cpuCount=0
            for line in cmd.result.output.splitlines()[1:]:
              words = line.split()[0:]
              if 'cpu' in words[0]:
                cpuCount+=1

            if cpuCount:
              idleCpuPerCpu = float(cmd.result.output.splitlines()[0].split()[4])/float(cpuCount)
            else:
              idleCpuPerCpu = None

            values = cmd.result.output.splitlines()[0].split()[1:]

            valueMap = dict(zip(ids, values))
            valueMap['ssCpuIdlePerCpu']=idleCpuPerCpu
        
            for id in valueMap:
        
                if datapointMap.has_key(id):
                    result.values.append((datapointMap[id], long(valueMap[id])))
        
        return result
