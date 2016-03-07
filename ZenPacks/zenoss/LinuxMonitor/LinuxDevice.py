##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.Zuul import getFacade
from zenoss.protocols.protobufs.zep_pb2 import (
    SEVERITY_CRITICAL, SEVERITY_ERROR,
    STATUS_NEW, STATUS_ACKNOWLEDGED, STATUS_SUPPRESSED,
    )

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

    def status(self):
        """Returns True if up, False if down.

        The value returned by this method is used to determine the
        "device status" shown in the top summary bar on the device screen.

        What up and down means can be subjective. What we've decided for a
        device monitored by default using SSH with periodic ping checks is that
        it a device that is up has no critical events in the /Cmd/Fail or
        /Status/Ping event classes.

        """
        if not self.monitorDevice():
            return None

        zep = getFacade("zep")
        fltr = zep.createEventFilter(
            element_identifier=self.id,
            element_sub_identifier=("zencommand", ""),
            event_class=("/Cmd/Fail", "/Status/Ping"),
            severity=(SEVERITY_CRITICAL, SEVERITY_ERROR),
            status=(STATUS_NEW, STATUS_ACKNOWLEDGED, STATUS_SUPPRESSED))

        events = zep.getEventSummaries(0, limit=1, filter=fltr)
        return events.get('total', 0) == 0
