###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser

class cpu(CommandParser):

    def processResults(self, cmd, result):
        """
        Process the results of "cat /proc/stat".  Take the first line (the cpu
        line) and pick out the values for the various datapoints.
        """
        
        datapointMap = dict([(dp.id, dp) for dp in cmd.points])
        
        # ssCpuSteal does not show up on all systems
        ids = ['ssCpuUser',
               'ssCpuNice',
               'ssCpuSystem',
               'ssCpuIdle',
               'ssCpuWait',
               'ssCpuInterrupt',
               'ssCpuSoftInterrupt',
               'ssCpuSteal']
                   
        values = cmd.result.output.splitlines()[0].split()[1:]
        valueMap = dict(zip(ids, values))
        
        for id in valueMap:
        
            if datapointMap.has_key(id):
                result.values.append((datapointMap[id], long(valueMap[id])))
        
        return result
