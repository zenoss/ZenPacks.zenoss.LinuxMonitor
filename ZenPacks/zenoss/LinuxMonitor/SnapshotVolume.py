##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import schema

import logging

from Products.Zuul.interfaces import ICatalogTool
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
LOG = logging.getLogger('zen.lvm.SnapshotVolume')


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

        # self.name(): snapshot-366fc7b1-4c11-4ae6-9ec2-d096df0194e0
        return ['cinder.lvm:snapshotvolume|%s' % (self.name())]

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
        results = ICatalogTool(self.device()).search('Products.ZenModel.FileSystem.FileSystem')
        for brain in results:
            fs = brain.getObject()
            if fs.title == self.mountpoint:
                return fs
        return None
