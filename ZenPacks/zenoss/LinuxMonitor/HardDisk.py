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
    major_minor = None
    size = None
    mount = None

    _properties = BaseHardDisk._properties + (
        {'id': 'size', 'label': 'Size',
            'type': 'string', 'mode': 'w'},
        {'id': 'major_minor', 'type': 'string',
            'mode': 'w'},
        {'id':'mount', 'type': 'string',
            'mode':'w'}
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
        return physicalvolumes

    def getRRDTemplateName(self):
            return "HardDisk"
