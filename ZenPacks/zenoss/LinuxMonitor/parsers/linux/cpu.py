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
                   'ssCpuUserPerCpu',
                   'ssCpuSystemPerCpu',
                   'ssCpuIdlePerCpu',
                   'ssCpuUsedPerCpu',
                   'ssCpuWaitPerCpu']

            # New ids for Device CPU
            userCpuPerCpu = None
            systemCpuPerCpu = None
            idleCpuPerCpu = None
            usedCpuPerCpu = None
            waitCpuPerCpu = None

            # Component cpu returns socket value, device cpu return empty str
            component = getattr(cmd, 'component', None)

            # Calculate the number of CPUs
            cpuCount=0
            single_cpu_line = ''
            for line in cmd.result.output.splitlines()[1:]:
              words = line.split()[0:]
              if 'cpu' in words[0]:
                cpuCount+=1
                if component:
                  if component == line[3]:
                    # If component, we matched the socket
                    single_cpu_line = line
                    break

            # Check if component or device cpu monitoting
            if component:
                perCpuValues = single_cpu_line.split()
                # usedCpuPerCpu = userCpu + systemCpu
                usedCpuPerCpu = float(perCpuValues[1]) + float(perCpuValues[3])
            else:
                # If we got a CPU count, set the normalized perCpu values
                if cpuCount:
                  perCpuValues = cmd.result.output.splitlines()[0].split()
                  userCpuPerCpu = float(perCpuValues[1]) / float(cpuCount)
                  systemCpuPerCpu = float(perCpuValues[3]) / float(cpuCount)
                  idleCpuPerCpu = float(perCpuValues[4]) / float(cpuCount)
                  usedCpuPerCpu = userCpuPerCpu + systemCpuPerCpu
                  waitCpuPerCpu = float(perCpuValues[5]) / float(cpuCount)

            values = perCpuValues[1:]

            valueMap = dict(zip(ids, values))
            valueMap['ssCpuUserPerCpu']=userCpuPerCpu
            valueMap['ssCpuSystemPerCpu']=systemCpuPerCpu
            valueMap['ssCpuIdlePerCpu']=idleCpuPerCpu
            valueMap['ssCpuUsedPerCpu']=usedCpuPerCpu
            valueMap['ssCpuWaitPerCpu']=waitCpuPerCpu

            for id in valueMap:
                if datapointMap.has_key(id):
                    result.values.append((datapointMap[id], long(valueMap[id])))
        return result
