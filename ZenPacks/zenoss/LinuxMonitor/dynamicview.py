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

from ZenPacks.zenoss.DynamicView import TAG_ALL, TAG_IMPACTED_BY, TAG_IMPACTS
from ZenPacks.zenoss.DynamicView.interfaces import IRelatable
from ZenPacks.zenoss.DynamicView.interfaces import IRelationsProvider
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

from .FileSystem import FileSystem
from .HardDisk import HardDisk


class FileSystemRelatable(BaseRelatable):

    implements(IRelatable)
    adapts(FileSystem)

    group = "File Systems"


class FileSystemRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(FileSystem)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            # Either LogicalVolume, HardDisk or Device.
            impacting_object = self._adapted.impacting_object()
            if impacting_object:
                yield self.constructRelationTo(
                    impacting_object,
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
            # One of FileSystem, PhysicalVolume, or LogicalVolume.
            impacted_object = self._adapted.impacted_object()
            if impacted_object:
                yield self.constructRelationTo(impacted_object, TAG_IMPACTS)
