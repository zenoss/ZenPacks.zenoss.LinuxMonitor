##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

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

    def all_cpus(self):
        """Generate all CPU components."""
        for cpu in self.hw.cpus():
            yield cpu

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

    def is_hypervisor(self):
        if hasattr(self, 'openstack_hostComponent'):
            if self.openstack_hostComponent():
                return True

        return False

    def getDynamicViewGroup(self):
        """Return DynamicView group information.

        Overrides zenpack.yaml to distinguish between standard devices, and
        devices potentially running other devices as guests. Devices on which
        other devices run need a different group name, and a higher weight.

        """
        if self.is_hypervisor():
            return {
                "name": "Devices (Hypervisor)",
                "weight": 550,
                "type": self.zenpack_name,
                "icon": self.icon_url,
                }
        else:
            return {
                "name": "Devices",
                "weight": 50,
                "type": self.zenpack_name,
                "icon": self.icon_url,
                }
