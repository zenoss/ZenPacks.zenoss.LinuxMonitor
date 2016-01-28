######################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################


from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.guid.interfaces import IGlobalIdentifier
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider

from Products.ZenModel.CPU import CPU
from Products.ZenModel.FileSystem import FileSystem


class BaseRelationsProvider(object):
    relationship_provider = "LinuxMonitor"

    def __init__(self, adapted):
        self._object = adapted

    def belongsInImpactGraph(self):
        return True


class CPURelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(CPU)

    def getEdges(self):
        cpu = self._object
        device = cpu.device()
        if device.getDeviceClassName() == '/Server/SSH/Linux':
            yield ImpactEdge(
                IGlobalIdentifier(device).getGUID(),
                IGlobalIdentifier(cpu).getGUID(),
                self.relationship_provider)


class FileSystemRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(FileSystem)

    def getEdges(self):
        filesystem = self._object
        device = filesystem.device()
        if device.getDeviceClassName() == '/Server/SSH/Linux':
            yield ImpactEdge(
                IGlobalIdentifier(device).getGUID(),
                IGlobalIdentifier(filesystem).getGUID(),
                self.relationship_provider)

