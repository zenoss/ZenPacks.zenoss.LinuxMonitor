###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################


import re

from CollectorPlugin import CommandPlugin


class cpuinfo(CommandPlugin):
    """
    cat /proc/cpuinfo - get CPU information on Linux machines
    """
    
    maptype = "CPUMap"
    command = "/bin/cat /proc/cpuinfo"
    compname = "hw"
    relname = "cpus"
    modname = "Products.ZenModel.CPU"
    
    pattern = re.compile(r"\s*processor\s+:\s+")
    linePattern = re.compile(r"\s*:\s*")
    
    def process(self, device, results, log):
        log.info('Collecting CPU information for device %s' % device.id)
        rm = self.relMap()
        
        for result in self.pattern.split(results)[1:]:
            lines = result.splitlines()
            pairs = []
            for line in lines[1:]:
                if line:
                    pair = self.linePattern.split(line)
                    if len(pair) == 2: pairs.append(pair)
            cpuinfo = dict(pairs)
            om = self.objectMap()
            om.id = lines[0].strip()
            om.clockspeed = cpuinfo["cpu MHz"]
            om.cacheSizeL2 = cpuinfo["cache size"].split()[0]
            om.setProductKey = " ".join([cpuinfo["vendor_id"], 
                                         cpuinfo["model name"]])
            rm.append(om)
            
        return [rm]
