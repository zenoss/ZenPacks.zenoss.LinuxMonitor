##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools

from Products.ZenUtils.Utils import prepId
from Products.Zuul.interfaces import ICatalogTool
from Products.AdvancedQuery import Eq, Or

from . import schema


class HardDisk(schema.HardDisk):

    """Model class for HardDisk.

    Instances of this class get stored in ZODB.

    """

    def filesystem(self):
        """Return filesystem mounting this disk."""
        try:
            # Assumes all FileSystem ids are prepId(mount). Currently they are.
            return self.device().os.filesystems._getOb(prepId(self.mount))
        except Exception:
            pass

    def physicalVolume(self):
        results = self.device().search('PhysicalVolume', harddisk_id=self.id)
        for result in results:
            try:
                return result.getObject()
            except Exception:
                pass

    def logicalVolume(self):
        """Return LogicalVolume associated with this disk.

        This only works when the disk is an lvm type, not a real disk.

        """
        if not self.major_minor:
            return

        results = itertools.chain.from_iterable(
            self.device().search(name, major_minor=self.major_minor)
            for name in ('LogicalVolume', 'SnapshotVolume'))

        for result in results:
            try:
                return result.getObject()
            except Exception:
                pass

    def impacted_object(self):
        """Return impacted PhysicalVolume, LogicalVolume, or FileSystem.

        A HardDisk can impact one of PhysicalVolume, LogicalVolume, or
        FileSystem depending on what type of block device it is. This method
        will return the proper object, or None.

        """
        fs = self.filesystem()
        if fs:
            return fs

        pv = self.physicalVolume()
        if pv:
            return pv

        lv = self.logicalVolume()
        if lv:
            return lv

    def storage_disk_lun(self):
        # return the UCS storage disk/virtual drive
        # if disk_ids contains the IDs of disk/virtual drive
        if self.disk_ids:
            results = ICatalogTool(self.getDmdRoot('Devices')).search(
                query=Or(*[Eq('searchKeywords', id)
                           for id in self.disk_ids]))

            for brain in results:
                try:
                    yield brain.getObject()
                except Exception:
                    continue
