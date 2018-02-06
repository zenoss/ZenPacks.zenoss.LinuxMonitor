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
from ZenPacks.zenoss.LinuxMonitor.util import override_graph_labels


class VolumeGroup(schema.VolumeGroup):

    def utilization(self):
        try:
            vgsize = int(self.cacheRRDValue('group_size', None))
            vgfree = int(self.cacheRRDValue('group_free', None))
        except Exception:
            return 'Unknown'

        if vgsize == 0:
            return 'Unknown'

        return '{}%'.format(int(float(vgsize - vgfree) / vgsize * 100))

    def snapshot_volumes(self):
        count = 0
        for lv in self.logicalVolumes():
            count += len(lv.snapshotVolumes())

        return '{}'.format(count)

    def getDefaultGraphDefs(self, drange=None):
        # Add and re-label graphs displayed in other components
        graphs = super(VolumeGroup, self).getDefaultGraphDefs(drange)

        for pv in self.physicalVolumes():
            pvGraphs = override_graph_labels(pv, drange)
            graphs.extend(pvGraphs)

        return graphs

    def getGraphObjects(self):
        graphs = super(VolumeGroup, self).getGraphObjects()

        for pv in self.physicalVolumes():
            graphs.extend(pv.getGraphObjects())

        return graphs
