##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools

from zope.interface import implements

from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos.component.filesystem import FileSystemInfo as BaseFileSystemInfo
from Products.Zuul.interfaces.component import IFileSystemInfo as IBaseFileSystemInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from . import zenpacklib


class FileSystem(BaseFileSystem):

    """Model class for FileSystem.

    Instances of this class get stored in ZODB.

    """

    meta_type = 'LinuxFileSystem'

    logicalvolume = None

    _properties = BaseFileSystem._properties + (
        {'id': 'logicalvolume', 'label': 'Logical Volume', 'type': 'string'},
        )

    def getLogicalVolume(self):
        if not self.mount:
            return

        results = itertools.chain.from_iterable(
            zenpacklib.catalog_search(
                self.device(),
                name,
                mountpoint=self.mount)
            for name in ('LogicalVolume', 'SnapshotVolume'))

        for result in results:
            try:
                return result.getObject()
            except Exception:
                pass

    def getBlockDevice(self):
        device = self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            obj = brain.getObject()
            if obj.mount == self.mount:
                return obj

    def getRRDTemplateName(self):
        return "FileSystem"

    def getDefaultGraphDefs(self, drange=None):
        graphs = super(FileSystem, self).getDefaultGraphDefs()
        comp = self.getBlockDevice()
        if comp:
            for graph in comp.getDefaultGraphDefs(drange):
                graphs.append(graph)
        return graphs

    def getGraphObjects(self):
        graphs = super(FileSystem, self).getGraphObjects()
        comp = self.getBlockDevice()
        if comp:
            for graph in comp.getGraphObjects():
                graphs.append(graph)
        return graphs

    def getIconPath(self):
        '''
        Return the path to an icon for this component.
        '''
        return '/++resource++linux/img/file-system.png'


class IFileSystemInfo(IBaseFileSystemInfo):

    """IInfo interface for FileSystem.

    This is used for JSON API definition. Fields described here are what will
    appear on instance's component details panel.

    """

    logicalVolume = schema.Entity(
        title=_t(u"LVM Logical Volume"),
        group="Details",
        readonly=True)

    blockDevice = schema.Entity(
        title=_t(u"Block Device"),
        group="Details",
        readonly=True)


class FileSystemInfo(BaseFileSystemInfo):

    """Info adapter for FileSystem.

    This is used for API implementation and JSON serialization. Properties
    implemented here will be available through the JSON API.

    """

    implements(IFileSystemInfo)

    @property
    @info
    def logicalVolume(self):
        return self._object.getLogicalVolume()

    @property
    @info
    def blockDevice(self):
        return self._object.getBlockDevice()
