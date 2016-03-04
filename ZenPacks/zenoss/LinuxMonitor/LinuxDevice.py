##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.Zuul import getFacade

from . import schema

from .FileSystem import FileSystem


class LinuxDevice(schema.LinuxDevice):

    """Model class for evice.

    Extends Device defined in zenpack.yaml.

    """

    def all_harddisks(self):
        """Generate all HardDisk components."""
        for hd in self.hw.harddisks():
            yield hd

    def all_processes(self):
        """Generate all OSProcess components."""
        for process in self.os.processes():
            yield process

    def all_ipservices(self):
        """Generate all IpService components."""
        for ipservice in self.os.ipservices():
            yield ipservice

    def impacted_filesystems(self):
        """Generate filesystems impacted by this device.

        The filesystems on a device can either be impacted by their underlying
        HardDisk, LogicalVolume, or in the absence of either of those, its
        Device. This method only generates filesystems that themselves claim to
        be impacted by their device.

        """
        for fs in self.os.filesystems():
            if isinstance(fs, FileSystem):
                if fs.impacting_object() == self:
                    yield fs

    def getPingStatus(self):
        """Returns 0 if up, 1 if down.

        Overridden to use both /Status/Ping and /Cmd/Fail event classes as a
        basis for determining if the device is up or down.

        """
        zep = getFacade('zep')
        fltr = zep.createEventFilter(
            element_identifier=self.id,
            event_class=('/Cmd/Fail', '/Status/Ping'),
            severity=(4, 5), status=(0, 1, 2))

        events = zep.getEventSummaries(0, filter=fltr)
        try:
            events['events'].next()
            return 1
        except StopIteration:
            return 0
