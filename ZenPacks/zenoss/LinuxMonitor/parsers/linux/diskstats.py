##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2009, all rights reserved.
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
        
        ssIORawReceived, ssIORawSent
        
        
    Example command output:
        
        ...
        1   14 ram14 0 0 0 0 0 0 0 0 0 0 0
        1   15 ram15 0 0 0 0 0 0 0 0 0 0 0
        8    0 sda 2419270 2387883 66904427 33826350 6127156 23952335 240718108 81693197 1 33303827 115529971
        8    1 sda1 1371 2752 26 52
        8    2 sda2 4807027 66901259 30089735 240717776
        8   16 sdb 1826581 184642 64009266 26696906 16272358 19732741 288156896 442269902 0 26365198 468964973
        ...
        
"""
import re
from collections import namedtuple
from Products.ZenRRD.CommandParser import CommandParser

import logging
log = logging.getLogger('zen.command.parsers.diskstats')

# datafields in /proc/diskstats, per http://www.kernel.org/doc/Documentation/iostats.txt
DiskStatsData = namedtuple("DiskStatsData", 
    "total_reads  num_reads_merged  total_sectors_read    total_ms_reading "
    "total_writes num_writes_merged total_sectors_written total_ms_writing "
    "num_io_in_progess  total_ms_io  weighted_ms_per_io")

OUTPUT_DATA_KEYS = ["ssIORawReceived", "ssIORawSent"]

_reCache = {}
def _getReMatcher(regex):
    if regex not in _reCache:
        try:
            _reCache[regex] = re.compile(regex).match
        except Exception:
            _reCache[regex] = None
    return _reCache[regex]        

def _parseOutput(output, hdFilterFn=None):
    """
    Given "/proc/diskstats" output, filter out logical devices and find the
    sum read sectors and write sectors of the physical devices. Return a
    mapping of "ssIORawReceived" to that line's reads sectors and 
    "ssIORawSent" to that line's writes sectors.
    """
    # if no filtering function given, accept anything
    if hdFilterFn is None:
        hdFilterFn = lambda s: True

    totalReadSectors = 0
    totalWrittenSectors = 0
    
    for line in output.strip().splitlines():

        words = line.split()

        # some logical devices have length less than 14
        # other logical devices start with dm-
        if len(words) == 14:
            diskid = words[2]
            if hdFilterFn(diskid) and not diskid.startswith("dm-"):
                diskstatsdata = DiskStatsData(*words[3:])
                log.debug("extracted data for device '%s': %s", diskid, diskstatsdata)
                totalReadSectors    += int(diskstatsdata.total_sectors_read)
                totalWrittenSectors += int(diskstatsdata.total_sectors_written)
    
    return dict(zip(OUTPUT_DATA_KEYS, (totalReadSectors, totalWrittenSectors)))

class diskstats(CommandParser):

    HARD_DISK_MATCH_PROPERTY = 'zHardDiskMapMatch'

    def dataForParser(self, context, datapoint):
        ret = super(diskstats, self).dataForParser(context, datapoint)

        # save global zHardDiskMapMatch filtering regex property, 
        # to be copied to each datapoint's .data attribute
        ret['hdFilterRegex'] = getattr(context, self.HARD_DISK_MATCH_PROPERTY, None)

        return ret

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
        pointsMap = dict((dp.id, dp) for dp in cmd.points)
        destkeys = [key for key in OUTPUT_DATA_KEYS if key in pointsMap]

        # only bother parsing if there is some data of interest to be parsed
        if destkeys:

            # see if a filtering regex was attached to the datapoints - just look
            # at the first point, all will have the same value attached
            hdRegex= cmd.points[0].data['hdFilterRegex']
            log.debug("using hdRegex: %s", hdRegex)
            hdFilterFn = None
            if hdRegex:
                try:
                    hdFilterFn = _getReMatcher(hdRegex)
                except Exception as e:
                    log.warning("%s ignored, invalid regex specified: %s", self.HARD_DISK_MATCH_PROPERTY, e)

            # parse command output to extract values
            log.debug("about to parse: %s", cmd.result.output)
            valueMap = _parseOutput(cmd.result.output, hdFilterFn)

            # save (datapoint, value) tuples to result values
            result.values.extend((pointsMap[key], valueMap[key]) for key in destkeys)
            log.debug("parsed values: %s", zip(destkeys, (x[1] for x in result.values[-len(destkeys):])))

        return result
