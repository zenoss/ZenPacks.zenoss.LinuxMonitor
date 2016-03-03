##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""DynamicView adapters for LinuxMonitor.

This module depends on DynamicView implicitly and assumes it won't be imported
unless DynamicView is installed. This is accomplished by being registered in a
conditional ZCML section in configure.zcml.

"""

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.Device import Device

from ZenPacks.zenoss.DynamicView import TAG_ALL, TAG_IMPACTED_BY, TAG_IMPACTS
from ZenPacks.zenoss.DynamicView.interfaces import IRelatable
from ZenPacks.zenoss.DynamicView.interfaces import IRelationsProvider
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

from .FileSystem import FileSystem
from .HardDisk import HardDisk


class DeviceRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(Device)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for filesystem in self._adapted.os.filesystems():
                if isinstance(filesystem, FileSystem):
                    hd = filesystem.getBlockDevice()
                    lv = filesystem.getLogicalVolume()
                    if not any((hd, lv)):
                        yield self.constructRelationTo(filesystem, TAG_IMPACTS)

            for harddisk in self._adapted.hw.harddisks():
                if isinstance(harddisk, HardDisk):
                    yield self.constructRelationTo(harddisk, TAG_IMPACTS)


class FileSystemRelatable(BaseRelatable):

    implements(IRelatable)
    adapts(FileSystem)

    group = "File Systems"


class FileSystemRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(FileSystem)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            lv = self._adapted.getLogicalVolume()
            if lv:
                yield self.constructRelationTo(lv, TAG_IMPACTED_BY)
                return

            bd = self._adapted.getBlockDevice()
            if bd:
                yield self.constructRelationTo(bd, TAG_IMPACTED_BY)
                return

            yield self.constructRelationTo(
                self._adapted.device(),
                TAG_IMPACTED_BY)


class HardDiskRelatable(BaseRelatable):

    implements(IRelatable)
    adapts(HardDisk)

    group = "Hard Disks"


class HardDiskRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(HardDisk)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(
                self._adapted.device(),
                TAG_IMPACTED_BY)

        if type in (TAG_ALL, TAG_IMPACTS):
            pv = self._adapted.getPhysicalVolume()
            if pv:
                yield self.constructRelationTo(pv, TAG_IMPACTS)
                return

            lv = self._adapted.getLogicalVolume()
            if lv:
                yield self.constructRelationTo(lv, TAG_IMPACTS)
                return

            fs = self._adapted.getFileSystem()
            if fs and not fs.getLogicalVolume():
                yield self.constructRelationTo(fs, TAG_IMPACTS)
