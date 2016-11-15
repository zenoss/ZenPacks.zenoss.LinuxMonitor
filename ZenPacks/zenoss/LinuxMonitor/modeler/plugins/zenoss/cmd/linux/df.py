##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import re
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.ZenUtils.IpUtil import getHostByName


class df(CommandPlugin):
    maptype = "FilesystemMap"
    command = '/bin/df -PTk'
    compname = "os"
    relname = "filesystems"
    modname = "ZenPacks.zenoss.LinuxMonitor.FileSystem"
    deviceProperties = \
        CommandPlugin.deviceProperties + ('zFileSystemMapIgnoreNames',)

    oses = ['Linux', 'Darwin', 'SunOS', 'AIX']

    def condition(self, device, log):
        return device.os.uname == '' or device.os.uname in self.oses

    def process(self, device, results, log):
        log.info('Collecting filesystems for device %s' % device.id)
        skipfsnames = getattr(device, 'zFileSystemMapIgnoreNames', None)
        rm = self.relMap()
        rlines = results.split("\n")
        bline = ""
        for line in rlines:
            if line.startswith("Filesystem"):
                continue
            om = self.objectMap()
            spline = line.split()
            if len(spline) == 1:
                bline = spline[0]
                continue
            if bline:
                spline.insert(0, bline)
                bline = None
            if len(spline) != 7:
                continue

            storage_device = spline[0]
            if ':' in storage_device:
                try:
                    server, junction_point = storage_device.rsplit(':', 1)
                    om.server_name = server
                    spline[0] = '{0}:{1}'.format(
                        getHostByName(server), junction_point
                    )
                except(Exception):
                    spline[0] = storage_device

            (om.storageDevice, om.type, tblocks, u, a, p, om.mount) = spline
            if skipfsnames and re.search(skipfsnames, om.mount):
                continue

            if tblocks == "-":
                om.totalBlocks = 0
            else:
                try:
                    om.totalBlocks = long(tblocks)
                except ValueError:
                    # Ignore this filesystem if what we thought was total
                    # blocks isn't a number.
                    continue

            om.blockSize = 1024
            om.id = self.prepId(om.mount)
            om.title = om.mount
            rm.append(om)
        return [rm]
