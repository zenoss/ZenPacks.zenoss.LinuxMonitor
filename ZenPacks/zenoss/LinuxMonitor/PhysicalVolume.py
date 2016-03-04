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

    def blockDevice(self):
        try:
            return self.device().hw.harddisks._getOb(self.harddisk_id)
        except Exception:
            pass

    def getDefaultGraphDefs(self, drange=None):
        graphs = super(PhysicalVolume, self).getDefaultGraphDefs(drange)

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getDefaultGraphDefs(drange))

        return graphs

    def getGraphObjects(self):
        graphs = super(PhysicalVolume, self).getGraphObjects()

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getGraphObjects())

        return graphs
