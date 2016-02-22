##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.HardDisk import HardDisk as BaseHardDisk
from . import zenpacklib


class HardDisk(BaseHardDisk):
    meta_type = 'LinuxHardDisk'

    _properties = BaseHardDisk._properties + (
        {'id': 'physicalvolumes', 'label': 'Physical Volumes',
            'type': 'entity', 'mode': 'w'},
        {'id': 'size', 'label': 'Size',
            'type': 'string', 'mode': 'w'}
        )

    def getPhysicalVolumes(self):
        results = zenpacklib.catalog_search(
            self.device(),
            'PhysicalVolume',
            harddisk_id=self.id)
        physicalvolumes = []
        for result in results:
            try:
                physicalvolumes.append(result.getObject())
            except Exception:
                pass
        self.physicalvolumes = physicalvolumes
        return physicalvolumes

    def getRRDTemplateName(self):
            return "HardDisk"
