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

def getReadWriteSectors(line):
    """
    Given a line of "vmstat -d" output, return the line's reads sectors and
    writes sectors.
    """
    return [int(word) for word in line.split()[3:8:4]]

def parseOutput(output):
    """
    Given "vmstat -d" output, find the line with the max read sectors and
    return a mapping of "ssIORawReceived" to that line's reads sectors and 
    "ssIORawSent" to that line's writes sectors.
    """
    lines = output.strip().split("\n")[2:]
    readWrites = [getReadWriteSectors(line) for line in lines]
    ssIORawReceived, ssIORawSent = sorted(readWrites)[-1]
    return dict(ssIORawReceived=ssIORawReceived, ssIORawSent=ssIORawSent)

class vmstatd(CommandParser):
    
    def processResults(self, cmd, result):
        """
        Given "vmstat -d" output, find the line with the max read sectors. Assign
        that line's reads sectors to ssIORawReceived and writes sectors to
        ssIORawSent. Here is an example of the command's output:
        
        disk- ------------reads------------ ------------writes----------- -----IO------
               total merged sectors      ms  total merged sectors      ms    cur    sec
        ram0       0      0       0       0      0      0       0       0      0      0
        sda    38093   5468  685209  277174  72151 108618 1446156 5482764      0    608
        
        in this case [685209, 1446156] would be returned.
        """
        valueMap = parseOutput(cmd.result.output)
        pointsMap = dict([(dp.id, dp) for dp in cmd.points])
        for key in valueMap:
            if pointsMap.has_key(key):
                result.values.append((pointsMap[key], valueMap[key]))
        return result
