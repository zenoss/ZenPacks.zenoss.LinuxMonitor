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
from Products.ZenModel.OSProcess import OSProcess
from Products.ZenModel.IpService import IpService
from ZenPacks.zenoss.LinuxMonitor.LinuxDevice import LinuxDevice
from ZenPacks.zenoss.LinuxMonitor.FileSystem import FileSystem


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
        if isinstance(device, LinuxDevice):
            yield ImpactEdge(
                IGlobalIdentifier(device).getGUID(),
                IGlobalIdentifier(cpu).getGUID(),
                self.relationship_provider)


class OSProcessRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(OSProcess)

    def getEdges(self):
        os_process = self._object
        device = os_process.device()
        if isinstance(device, LinuxDevice):
            yield ImpactEdge(
                IGlobalIdentifier(device).getGUID(),
                IGlobalIdentifier(os_process).getGUID(),
                self.relationship_provider)


class IpServiceRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(IpService)

    def getEdges(self):
        ip_service = self._object
        device = ip_service.device()
        if isinstance(device, LinuxDevice):
            yield ImpactEdge(
                IGlobalIdentifier(device).getGUID(),
                IGlobalIdentifier(ip_service).getGUID(),
                self.relationship_provider)


class DeviceRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(LinuxDevice)

    def getEdges(self):
        device = self._object
        for process in device.os.processes():
            yield ImpactEdge(IGlobalIdentifier(device).getGUID(),
                             IGlobalIdentifier(process).getGUID(),
                             self.relationship_provider)

        for ipservice in device.os.ipservices():
            yield ImpactEdge(IGlobalIdentifier(device).getGUID(),
                             IGlobalIdentifier(ipservice).getGUID(),
                             self.relationship_provider)

        for cpu in device.hw.cpus():
            yield ImpactEdge(IGlobalIdentifier(device).getGUID(),
                             IGlobalIdentifier(cpu).getGUID(),
                             self.relationship_provider)


class FileSystemRelationsProvider(BaseRelationsProvider):
    implements(IRelationshipDataProvider)
    adapts(FileSystem)

    def getEdges(self):
        file_system = self._object
        for storage_server in file_system.getStorageServer():
            yield ImpactEdge(IGlobalIdentifier(storage_server).getGUID(),
                             IGlobalIdentifier(file_system).getGUID(),
                             self.relationship_provider)
