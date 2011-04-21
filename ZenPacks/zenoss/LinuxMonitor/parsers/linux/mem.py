###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser

MULTIPLIER = {
    'kB' : 1024,
    'MB' : 1024 * 1024,
    'b' : 1
}

class mem(CommandParser):

    def processResults(self, cmd, result):
        """
        Process the results of "cat /proc/meminfo".
        """
        datapointMap = dict([(dp.id, dp) for dp in cmd.points])
        data = [line.split(':') for line in cmd.result.output.splitlines()]
        
        for id, vals in data:
            if id in datapointMap:
                try:
                    value, unit = vals.strip().split()
                except:
                    value = vals
                    unit = 1
                size = int(value) * MULTIPLIER.get(unit, 1)
                result.values.append((datapointMap[id], size))
        
        return result

