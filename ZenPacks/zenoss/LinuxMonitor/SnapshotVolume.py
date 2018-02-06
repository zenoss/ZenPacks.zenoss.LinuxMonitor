##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from zope.interface import implements

from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.LinuxMonitor.util import override_graph_labels

from . import schema

try:
    from ZenPacks.zenoss.OpenStackInfrastructure.interfaces \
        import ICinderImplementationComponent
    from ZenPacks.zenoss.OpenStackInfrastructure.cinder_integration \
        import index_implementation_object, unindex_implementation_object, \
        get_cinder_components
    openstack = True
except ImportError:
    openstack = False


class SnapshotVolume(schema.SnapshotVolume):
    '''Class that handles logical volume snapshot
    '''
    if openstack:
        implements(ICinderImplementationComponent)

    # The "integration key(s)" for this component must be made up of
    # a set of values that uniquely identify this resource and are
    # known to both this zenpack and the openstack zenpack.  They may
    # involve modeled properties, zProperties, and values from the cinder
    # configuration files on the openstack host.
    def getCinderIntegrationKeys(self):
        # LVM snapshot would have a UUID as its id. But when
        # OpenStack creates a snapshot against a volume, OpenStack
        # will generate its own UUID for the snapshot and passes it on to LVM,
        # and the snapshot in LVM will have a UUID attached to it in its name

        # self.name(): _snapshot-366fc7b1-4c11-4ae6-9ec2-d096df0194e0
        snapshotname = self.name()
        if self.name().startswith('_'):
            snapshotname = self.name()[1:]
        return ['cinder.lvm:snapshotvolume|%s' % (snapshotname)]

    def index_object(self, idxs=None):
        super(SnapshotVolume, self).index_object(idxs=idxs)
        if openstack:
            index_implementation_object(self)

    def unindex_object(self):
        super(SnapshotVolume, self).unindex_object()
        if openstack:
            unindex_implementation_object(self)

    def openstack_core_components(self):
        # openstack infrastructure integration
        if openstack:
            return get_cinder_components(self)
        else:
            return []

    def filesystem(self):
        """Return filesystem mounting this logical volume."""
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
        graphs = super(SnapshotVolume, self).getDefaultGraphDefs(drange)

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
        graphs = super(SnapshotVolume, self).getGraphObjects()

        graphs.extend(self.volumeGroup().getGraphObjects())

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getGraphObjects())

        return graphs
