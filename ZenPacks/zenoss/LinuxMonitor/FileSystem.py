##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools
from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from . import zenpacklib


class FileSystem(BaseFileSystem):
    logicalvolume = None
    meta_type = 'LinuxFileSystem'

    _properties = BaseFileSystem._properties + (
        {'id': 'logicalvolume', 'label': 'Logical Volume',
            'type': 'string', 'mode': 'w'},
        )

    def getLogicalVolume(self):
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

    def getRRDTemplateName(self):
            return "FileSystem"

    def harddisk(self):
        device =self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            obj = brain.getObject()
            if obj.mount == self.mount:
                return obj

    def getDefaultGraphDefs(self, drange=None):
        graphs = super(FileSystem, self).getDefaultGraphDefs()
        comp = self.harddisk()
        if comp:
            for graph in comp.getDefaultGraphDefs(drange):
                graphs.append(graph)
        return graphs

    def getGraphObjects(self):
        graphs = super(FileSystem, self).getGraphObjects()
        comp = self.harddisk()
        if comp:
            for graph in comp.getGraphObjects():
                graphs.append(graph)
        return graphs
