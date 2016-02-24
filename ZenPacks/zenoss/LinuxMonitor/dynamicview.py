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

import logging

from zope.component import adapts
from zope.interface import implements

from ZenPacks.zenoss.DynamicView import TAG_ALL, TAG_IMPACTED_BY, TAG_IMPACTS
from ZenPacks.zenoss.DynamicView.interfaces import IRelationsProvider
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

from .FileSystem import FileSystem
from .HardDisk import HardDisk
LOG = logging.getLogger('zen.LinuxMonitor')


class FileSystemRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(FileSystem)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            lv = self._adapted.getLogicalVolume()
            if lv:
                yield self.constructRelationTo(lv, TAG_IMPACTED_BY)


class HardDiskRelationsProvider(BaseRelationsProvider):

    implements(IRelationsProvider)
    adapts(HardDisk)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for pv in self._adapted.getPhysicalVolumes():
                yield self.constructRelationTo(pv, TAG_IMPACTS)
