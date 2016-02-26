##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import schema

from zope.interface import implements

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
        for filesystem in self.device().os.filesystems():
            if filesystem.title == self.mountpoint:
                return filesystem

    def harddisk(self):
        device =self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            obj = brain.getObject()
            if obj.major_minor == self.major_minor:
                return obj

    def getDefaultGraphDefs(self, drange=None):
        graphs = super(LogicalVolume, self).getDefaultGraphDefs()
        comp = self.harddisk()
        if comp:
            for graph in comp.getDefaultGraphDefs(drange):
                graphs.append(graph)
        return graphs

    def getGraphObjects(self, drange=None):
        graphs = super(LogicalVolume, self).getGraphObjects()
        comp = self.harddisk()
        if comp:
            for graph in comp.getGraphObjects(drange):
                graphs.append(graph)
        return graphs
