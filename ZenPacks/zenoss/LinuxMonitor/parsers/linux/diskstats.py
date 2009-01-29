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

from Products.ZenRRD.CommandParser import CommandParser


READ_SECTORS_INDEX = 5
WRITTEN_SECTORS_INDEX = 9


def parseOutput(output):
    """
    Given "/proc/diskstats" output, filter out logical devices and find the
    sum read sectors and write sectors of the physical devices. Return a
    mapping of "ssIORawReceived" to that line's reads sectors and 
    "ssIORawSent" to that line's writes sectors.
    """
    totalReadSectors = 0
    totalWrittenSectors = 0
    
    for line in output.strip().splitlines():

        words = line.split()

        # some logical devices have length less than 14
        # other logical devices start with dm-
        if len(words) == 14 and not words[2].startswith("dm-"):
            totalReadSectors += int(words[READ_SECTORS_INDEX])
            totalWrittenSectors += int(words[WRITTEN_SECTORS_INDEX])
    
    return {"ssIORawReceived": totalReadSectors, 
            "ssIORawSent": totalWrittenSectors}

class diskstats(CommandParser):
    
    def processResults(self, cmd, result):
        """
        Given "/proc/diskstats" output, filter out any logical devices and sum
        the total read sectors and write sectors for all physical devices. 
        Assign the total read sectors to ssIORawReceived and the total write
        sectors to ssIORawSent. Here is an example of the command's output:

        1    0 ram0 0 0 0 0 0 0 0 0 0 0 0
        8    0 sda 10541549 14506876 290280380 125470349 29042916 90285293 954627734 801503911 0 134474409 926975991
        
        in this case [290280380, 954627734] would be returned.
        """
        valueMap = parseOutput(cmd.result.output)
        pointsMap = dict([(dp.id, dp) for dp in cmd.points])
        for key in valueMap:
            if pointsMap.has_key(key):
                result.values.append((pointsMap[key], valueMap[key]))
        return result
