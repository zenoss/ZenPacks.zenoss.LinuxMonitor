##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Linux Volume Groups

VolumeGroup class override
'''

from . import schema


class VolumeGroup(schema.VolumeGroup):

    def utilization(self):
        try:
            vgsize = int(self.cacheRRDValue('group_size', None))
            vgfree = int(self.cacheRRDValue('group_free', None))
        except Exception:
            return 'Unknown'

        if vgsize == 0:
            return 'Unknown'

        return '{}%'.format(int(float(vgsize-vgfree)/vgsize*100))

    def snapshot_volumes(self):
        count = 0
        for lv in self.logicalVolumes():
            count += len(lv.snapshotVolumes())

        return '{}'.format(count)
