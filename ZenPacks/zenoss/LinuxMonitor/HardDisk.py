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

from Products.ZenModel.HardDisk import HardDisk as BaseHardDisk
from Products.ZenUtils.Utils import prepId
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class HardDisk(BaseHardDisk):

    """Model class for HardDisk.

    Instances of this class get stored in ZODB.

    """

    class_label = "Hard Disk"
    class_plural_label = "Hard Disks"

    meta_type = 'LinuxHardDisk'

    size = None
    major_minor = None
    mount = None

    _properties = BaseHardDisk._properties + (
        {'id': 'size', 'label': 'Size', 'type': 'string'},
        {'id': 'major_minor', 'label': 'Major:Minor', 'type': 'string'},
        {'id': 'mount', 'label': 'Mount Point', 'type': 'string'},
        )

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

    def getRRDTemplateName(self):
        return "HardDisk"

    def getIconPath(self):
        '''
        Return the path to an icon for this component.
        '''
        return '/++resource++linux/img/hard-disk.png'


class IHardDiskInfo(IComponentInfo):

    """IInfo interface for HardDisk.

    This is used for JSON API definition. Fields described here are what will
    appear on instance's component details panel.

    """

    size = schema.Int(
        title=_t(u"Size"),
        group="Details",
        readonly=True)

    major_minor = schema.Text(
        title=_t(u"Major:Minor Number"),
        group="Details",
        readonly=True)

    physicalVolume = schema.Entity(
        title=_t(u"Physical Volume"),
        group="Details",
        readonly=True)


class HardDiskInfo(ComponentInfo):

    """Info adapter for HardDisk.

    This is used for API implementation and JSON serialization. Properties
    implemented here will be available through the JSON API.

    """

    implements(IHardDiskInfo)

    size = ProxyProperty('size')
    major_minor = ProxyProperty('major_minor')
    mount = ProxyProperty('mount')

    @property
    @info
    def filesystem(self):
        return self._object.filesystem()

    @property
    @info
    def physicalVolume(self):
        return self._object.physicalVolume()

    @property
    @info
    def logicalVolume(self):
        return self._object.logicalVolume()
