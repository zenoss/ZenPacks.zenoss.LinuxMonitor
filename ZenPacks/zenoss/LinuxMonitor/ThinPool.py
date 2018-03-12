##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from zope.interface import implements

from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.LinuxMonitor.util import override_graph_labels

from . import schema

class ThinPool(schema.ThinPool):
    '''Class that handles Thin Pools
    '''

    def filesystem(self):
        """Return filesystem mounting this Thin Pool."""
        try:
            # Assumes all FileSystem ids are prepId(mount). Currently they are.
            return self.device().os.filesystems._getOb(prepId(self.mountpoint))
        except Exception:
            pass

    def blockDevice(self):
        if not self.major_minor:
            return

        device = self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            try:
                obj = brain.getObject()
            except Exception:
                pass
            else:
                if obj.major_minor == self.major_minor:
                    return obj

    def getDefaultGraphDefs(self, drange=None):
        # Add and re-label graphs displayed in other components
        graphs = super(ThinPool, self).getDefaultGraphDefs(drange)

        vg = self.volumeGroup()
        if vg:
            vgGraphs = override_graph_labels(vg, drange)
            graphs.extend(vgGraphs)

        bd = self.blockDevice()
        if bd:
            bdGraphs = override_graph_labels(bd, drange)
            graphs.extend(bdGraphs)

        return graphs

    def getGraphObjects(self):
        graphs = super(ThinPool, self).getGraphObjects()

        graphs.extend(self.volumeGroup().getGraphObjects())

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getGraphObjects())

        return graphs
