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

    Command:

        cat /proc/diskstats


    Datapoints:

        Storage device:
            ssIORawReceived,
            ssIORawSent

        Partition:
            readsCompleted,
            readsMerged,
            sectorsRead,
            msReading,
            writesCompleted,
            writesMerged,
            sectorsWritten,
            msWriting,
            ioInProgress,
            msDoingIO,
            msDoingIOWeighted


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


import logging
import re

from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser


COMPONENT = r'(?P<component>([a-z]{1,2}d[a-z](\d+)?|c\d+t\d+d\d+s\d+|cciss\/c\dd\dp\d)\s)'
PARTITION = r'[a-z]{1,2}d[a-z]\d+$'
READS_COMPLETED = r'(?P<readsCompleted>\d+\s)'
READS_MERGED = r'(?P<readsMerged>\d+\s)'
SECTORS_READ = r'(?P<sectorsRead>\d+\s)'
MS_READING = r'(?P<msReading>\d+\s)'
WRITES_COMPLETED = r'(?P<writesCompleted>\d+\s)'
WRITES_MERGED = r'(?P<writesMerged>\d+\s)'
SECTORS_WRITTEN = r'(?P<sectorsWritten>\d+\s)'
MS_WRITING = r'(?P<msWriting>\d+\s)'
IO_IN_PROGESS = r'(?P<ioInProgress>\d+\s)'
MS_DOING_IO = r'(?P<msDoingIO>\d+\s)'
MS_DOING_IO_WEIGHTED = r'(?P<msDoingIOWeighted>\d+)'

SS_IO_RAW_RECEIVED = 'ssIORawReceived'
SS_IO_RAW_SENT = 'ssIORawSent'

PARTITION_DATAPOINTS = (SS_IO_RAW_RECEIVED, SS_IO_RAW_SENT)


LOG = logging.getLogger('zen.command.parsers.diskstats')


def compileHDRegex(userDefindHDRegex):
    try:
        compiledHDRegex = re.compile(userDefindHDRegex)
    except re.error:
        compiledHDRegex = re.compile(PARTITION)
    return compiledHDRegex


class diskstats(ComponentCommandParser):

    scanner = r''.join([COMPONENT, READS_COMPLETED, READS_MERGED,
                        SECTORS_READ, MS_READING,
                        WRITES_COMPLETED, WRITES_MERGED,
                        SECTORS_WRITTEN, MS_WRITING,
                        IO_IN_PROGESS, MS_DOING_IO, MS_DOING_IO_WEIGHTED])
    splitter = '\n'

    def dataForParser(self, context, datapoint):
        ret = super(diskstats, self).dataForParser(context, datapoint)
        ret['hdFilterRegex'] = getattr(context, 'zHardDiskMapMatch', None)
        ret['major_minor'] = getattr(context, 'major_minor', None)
        return ret

    def processResults(self, cmd, result):
        datapointMap = dict((dp.id, dp) for dp in cmd.points)
        if any((x in datapointMap for x in PARTITION_DATAPOINTS)):
            userDefindHDRegex = cmd.points[0].data.get('hdFilterRegex')
            hdRegex = compileHDRegex(userDefindHDRegex)
            parser = StorageDeviceParser(datapointMap, hdRegex)
        else:
            parser = PartitionParser(cmd.points)

        if cmd.points[0].data.get('major_minor'):
            major_minor = cmd.points[0].data.get('major_minor')
            pattern = r'(?P<component>{0}\s+{1}\s+\S+\s)'.format(
                *major_minor.split(':'))
            self.scanner =self.scanner.replace(COMPONENT, pattern)
            parser = BlockParser(cmd.points)

        LOG.debug("Parser class: %s, Scanner: %s",
                  parser.__class__, self.scanner)

        parts = cmd.result.output.split(self.splitter)
        for part in parts:
            match = re.search(self.scanner, part)
            if match:
                parser.parse(match)

        metrics = parser.getMetrics()
        LOG.debug("Parsed metrics: %s", metrics)
        if metrics:
            result.values.extend(metrics)

        return result


class Parser(object):

    def __init__(self):
        self._metrics = []

    def parse(self, datapointMap, match):
        for name, value in match.groupdict().items():
            dp = datapointMap.get(name, None)
            if dp:
                if value in ('-', ''):
                    value = 0
                self._metrics.append((dp, float(value)))

    def getMetrics(self):
        return self._metrics


class PartitionParser(Parser):

    def __init__(self, datapoints):
        super(PartitionParser, self).__init__()
        self._components = {}
        for dp in datapoints:
            dp.component = dp.data['componentScanValue']
            points = self._components.setdefault(dp.component, {})
            points[dp.id] = dp

    def parse(self, match):
        component = match.groupdict()['component'].strip()
        datapointMap = self._getDatapointMap(component)
        if datapointMap:
            super(PartitionParser, self).parse(datapointMap, match)

    def _getDatapointMap(self, component):
        for k, v in self._components.iteritems():
            if component == k.split('_')[1]:
                return v


class StorageDeviceParser(Parser):

    def __init__(self, datapointMap, hdRegex):
        super(StorageDeviceParser, self).__init__()
        self._datapointMap = datapointMap
        self._hdRegex = hdRegex
        self._sectorsRead = 0
        self._sectorsWritten = 0

    def parse(self, match):
        groupdict = match.groupdict()
        component = groupdict['component'].strip()
        if self._hdRegex.match(component):
            self._sectorsRead += int(groupdict['sectorsRead'])
            self._sectorsWritten += int(groupdict['sectorsWritten'])

    def getMetrics(self):
        self._metrics.append((
            self._datapointMap[SS_IO_RAW_RECEIVED], self._sectorsRead))
        self._metrics.append((
            self._datapointMap[SS_IO_RAW_SENT], self._sectorsWritten))
        return self._metrics


class BlockParser(Parser):

    def __init__(self, datapoints):
        self._metrics = []
        self._dataPointMap = dict((dp.id, dp) for dp in datapoints)

    def parse(self, match):
        for name, value in match.groupdict().items():
            dp = self._dataPointMap.get(name, None)
            if dp:
                if value in ('-', ''):
                    value = 0
                self._metrics.append((dp, float(value)))
