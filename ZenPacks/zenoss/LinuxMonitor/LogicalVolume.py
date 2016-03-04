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


class LogicalVolume(schema.LogicalVolume):
    '''Class that handles logical volume
    '''
    if openstack:
        implements(ICinderImplementationComponent)

    # The "integration key(s)" for this component must be made up of
    # a set of values that uniquely identify this resource and are
    # known to both this zenpack and the openstack zenpack.  They may
    # involve modeled properties, zProperties, and values from the cinder
    # configuration files on the openstack host.
    def getCinderIntegrationKeys(self):
        # LVM volume would have a UUID as its id. But when
        # OpenStack creates a LVM volume, OpenStack
        # will generate a UUID for the volume and passes it on to LVM,
        # and the volume in LVM will have a UUID attach to its name

        # self.name(): volume-366fc7b1-4c11-4ae6-9ec2-d096df0194e0
        return ['cinder.lvm:logicalvolume|%s' % (self.name())]

    def index_object(self, idxs=None):
        super(LogicalVolume, self).index_object(idxs=idxs)
        if openstack:
            index_implementation_object(self)

    def unindex_object(self):
        super(LogicalVolume, self).unindex_object()
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
        graphs = super(LogicalVolume, self).getDefaultGraphDefs(drange)

        graphs.extend(self.volumeGroup().getDefaultGraphDefs(drange))

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getDefaultGraphDefs(drange))

        return graphs

    def getGraphObjects(self):
        graphs = super(LogicalVolume, self).getGraphObjects()

        graphs.extend(self.volumeGroup().getGraphObjects())

        bd = self.blockDevice()
        if bd:
            graphs.extend(bd.getGraphObjects())

        return graphs
