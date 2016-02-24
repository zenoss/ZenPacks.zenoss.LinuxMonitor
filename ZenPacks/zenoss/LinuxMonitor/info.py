##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.Zuul.infos.component.filesystem import FileSystemInfo as BaseFileSystemInfo
from Products.Zuul.decorators import info
from zope.interface import implements
from ZenPacks.zenoss.LinuxMonitor.interfaces import IHardDiskInfo
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo


class HardDiskInfo(ComponentInfo):
    implements(IHardDiskInfo)

    size = ProxyProperty('size')

    @property
    @info
    def physicalvolumes_count(self):
        return len(self._object.getPhysicalVolumes())


class FileSystemInfo(BaseFileSystemInfo):

    @property
    @info
    def logicalvolume(self):
        return self._object.getLogicalVolume()
