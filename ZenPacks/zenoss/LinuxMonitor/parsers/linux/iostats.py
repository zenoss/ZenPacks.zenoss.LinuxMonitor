##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


"""
A command parser.

    http://www.kernel.org/doc/Documentation/iostats.txt

    Command: 

        cat /proc/diskstats


    Datapoints: 

        totalReads,
        numReadsMerged,
        totalSectorsRead,
        totalMsReading,
        totalWrites,
        numWritesMerged,
        totalSectorsWritten,
        totalMsWriting,
        numIOInProgess,
        totalMsIO,
        weightedMsPerIO


    Example command output:
        
           2       0 fd0 5 0 40 207 0 0 0 0 0 207 207
           8      16 sdb 27790 637 222124 40475 38 0 4347 88 0 36331 40535
           8      17 sdb1 27632 637 220860 40333 38 0 4347 88 0 36191 40393
           8       0 sda 32319 691 499909 108135 195490 9003 2410516 153855 0 121927 257759
           8       1 sda1 760 0 41316 613 525 0 4144 80 0 401 693
           8       2 sda2 31403 691 457345 107446 194965 9003 2406372 153775 0 121519 256990
          11       0 sr0 0 0 0 0 0 0 0 0 0 0 0
         253       0 dm-0 230 0 1840 237 0 0 0 0 0 82 237
         253       1 dm-1 5393 0 242369 13478 203968 0 2406372 179808 0 51241 193296
         253       2 dm-2 225 0 1794 565 3 0 24 2 0 344 567
         253       3 dm-3 853 0 1514 2147 11 0 4107 37 0 463 2184
         253       4 dm-4 105 0 840 128 0 0 0 0 0 128 128
         253       5 dm-5 193 0 1544 208 1 0 8 1 0 209 209
         253       6 dm-6 196 0 1568 354 1 0 8 0 0 203 354
         253       7 dm-7 7 0 56 19 4 0 32 1 0 20 20
         253       8 dm-8 193 0 1544 260 1 0 8 0 0 260 260
         253       9 dm-9 822 0 1536 2108 5 0 7 1 0 289 2109
         253      10 dm-10 6 0 48 19 6 0 48 1 0 20 20

"""


import re

from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser


COMPONENT = r'(?P<component>[a-z]+\d+\s)'
TOTAL_READS = '(?P<totalReads>\d+\s)'
NUM_READS_MERGED = '(?P<numReadsMerged>\d+\s)'
TOTAL_SECTORS_READ = '(?P<totalSectorsRead>\d+\s)'
TOTAL_MS_READING = '(?P<totalMsReading>\d+\s)'
TOTAL_WRITES = '(?P<totalWrites>\d+\s)'
NUM_WRITES_MERGED = '(?P<numWritesMerged>\d+\s)'
TOTAL_SECTORS_WRITTEN = '(?P<totalSectorsWritten>\d+\s)'
TOTAL_MS_WRITING = '(?P<totalMsWriting>\d+\s)'
NUM_IO_IN_PROGESS = '(?P<numIOInProgess>\d+\s)'
TOTAL_MS_IO = '(?P<totalMsIO>\d+\s)'
WEIGHTED_MS_PER_IO = '(?P<weightedMsPerIO>\d+)'


def getPoints(component, components):
    for k, v in components.iteritems():
        if component in k:
            return v


class iostats(ComponentCommandParser):

    componentSplit = '\n'
    componentScanner = COMPONENT
    scanners = [
        r''.join([COMPONENT, TOTAL_READS, NUM_READS_MERGED, TOTAL_SECTORS_READ,
                  TOTAL_MS_READING, TOTAL_WRITES, NUM_WRITES_MERGED,
                  TOTAL_SECTORS_WRITTEN, TOTAL_MS_WRITING, NUM_IO_IN_PROGESS,
                  TOTAL_MS_IO, WEIGHTED_MS_PER_IO]),
    ]

    def processResults(self, cmd, result):
        components = {}
        for dp in cmd.points:
            dp.component = dp.data['componentScanValue']
            points = components.setdefault(dp.component, {})
            points[dp.id] = dp

        parts = cmd.result.output.split(self.componentSplit)
        for part in parts:
            match = re.search(self.componentScanner, part)
            if not match:
                continue

            component = match.groupdict()['component'].strip()
            points = getPoints(component, components)
            if not points:
                continue

            self.getMetrics(result, points, part)

        return result
