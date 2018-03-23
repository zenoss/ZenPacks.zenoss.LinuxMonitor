##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools

from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.Utils import prepId
from Products.Zuul.catalog.interfaces import IIndexableWrapper
from ZenPacks.zenoss.ZenPackLib.lib.wrapper.ComponentIndexableWrapper import \
    ComponentIndexableWrapper

from ZenPacks.zenoss.LinuxMonitor.util import keyword_search

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
        """Return a generator of the storage disks/virtual drives based on disk_ids."""
        keywords = set()
        if self.disk_ids:
            for disk_id in self.disk_ids:
                # Add disk_id to keywords to save compatibility with UCS storage
                keywords.add(disk_id)

                ldisk_id = disk_id.lower()
                if ldisk_id.startswith('wwn-0x'):
                    keywords.add(
                        'has-target-wwn:{}'.format(ldisk_id.lstrip('wwn-0x'))
                    )
        for obj in keyword_search(self.getDmdRoot('Devices'), keywords):
            yield obj


class HardDiskIndexableWrapper(ComponentIndexableWrapper):
    implements(IIndexableWrapper)
    adapts(HardDisk)

    def searchKeywordsForChildren(self):
        """Return tuple of search keywords for HardDisk objects."""
        keywords = set()
        disk_ids = self._context.disk_ids

        if disk_ids:
            for disk_id in disk_ids:
                ldisk_id = disk_id.lower()
                if ldisk_id.startswith('wwn-0x'):
                    # add uses-target-wwn keyword to make it possible to find
                    # this HardDisk from an appropriate storage provider
                    keywords.add(
                        'uses-target-wwn:{}'.format(ldisk_id.lstrip('wwn-0x'))
                    )

        return (super(HardDiskIndexableWrapper, self).searchKeywordsForChildren() +
                tuple(keywords))
