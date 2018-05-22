##############################################################################
#
# Copyright (C) Zenoss, Inc. 2008-2018, all rights reserved.
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

            # Component cpu returns socket value, device cpu return empty str
            component = getattr(cmd, 'component', None)

            # Calculate the number of CPUs
            cpuCount = 0
            single_cpu_line = ''

            for line in cmd.result.output.splitlines()[1:]:
                # line e.g. 'cpu0 21306 149059 1785 18404 88442 0 117231 0 0 0'
                words = line.split()[0:]
                if 'cpu' in words[0]:
                    cpuCount += 1
                    if component and (component == words[0][3:]):
                        # If component, we matched the socket
                        single_cpu_line = line
                        break

            valueMap = {}

            # Check if component or device cpu monitoring
            if component:
                perCpuValues = single_cpu_line.split()
                values = map(int, perCpuValues[1:])

                valueMap = {
                    'ssCpuUser': values[0],
                    'ssCpuNice': values[1],
                    'ssCpuSystem': values[2],
                    'ssCpuUsed': values[0] + values[1] + values[2],
                    'ssCpuIdle': values[3],
                    'ssCpuWait': values[4],
                    'ssCpuInterrupt': values[5],
                    'ssCpuSoftInterrupt': values[6],
                    'ssCpuSteal': values[7]}

            # If we got a CPU count, set the normalized perCpu values
            if not component and cpuCount:
                perCpuValues = cmd.result.output.splitlines()[0].split()
                values = [
                    float(value) / cpuCount for value in perCpuValues[1:]]

                valueMap = {
                    'ssCpuUserPerCpu': values[0],
                    'ssCpuNicePerCpu': values[1],
                    'ssCpuSystemPerCpu': values[2],
                    'ssCpuUsedPerCpu': values[0] + values[1] + values[2],
                    'ssCpuIdlePerCpu': values[3],
                    'ssCpuWaitPerCpu': values[4],
                    'ssCpuInterruptPerCpu': values[5],
                    'ssCpuSoftInterruptPerCpu': values[6],
                    'ssCpuStealPerCpu': values[7]}

            if not valueMap:
                return result

            for dp_id in valueMap:
                if dp_id in datapointMap:
                    result.values.append(
                        (datapointMap[dp_id], long(valueMap[dp_id])),)

        return result
