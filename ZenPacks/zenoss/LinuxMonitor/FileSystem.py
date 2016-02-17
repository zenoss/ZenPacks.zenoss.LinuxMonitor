##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from Products.Zuul.interfaces import ICatalogTool


class FileSystem(BaseFileSystem):
    logicalvolume = None
    meta_type = 'LinuxFileSystem'

    _properties = BaseFileSystem._properties + (
        {'id': 'logicalvolume', 'label': 'Logical Volume',
            'type': 'string', 'mode': 'w'},
        )

    def getLogicalVolume(self):
        results = ICatalogTool(self.device()).search(
            ('ZenPacks.zenoss.LinuxMonitor.LogicalVolume.LogicalVolume',
             'ZenPacks.zenoss.LinuxMonitor.SnapshotVolume.SnapshotVolume'))
        for brain in results:
            lv = brain.getObject()
            if lv.dm_path == self.storageDevice:
                return lv
        return None
