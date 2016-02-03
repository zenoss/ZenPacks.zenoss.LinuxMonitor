##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Linux Volume Manager

PhysicalVolume class override
'''

from . import schema


class PhysicalVolume(schema.PhysicalVolume):

    def utilization(self):
        try:
            pvsize = int(self.cacheRRDValue('volume_size', None))
            pvfree = int(self.cacheRRDValue('volume_free', None))
        except Exception:
            return 'Unknown'

        if pvsize == 0:
            return 'Unknown'

        return '{}%'.format(int(float(pvsize-pvfree)/pvsize*100))
