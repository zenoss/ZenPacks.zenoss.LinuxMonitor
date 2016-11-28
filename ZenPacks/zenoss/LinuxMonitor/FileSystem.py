##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools

from zope.component import adapts
from zope.interface import implements

from zExceptions import NotFound

from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from Products.ZenUtils.FunctionCache import FunctionCache
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.catalog.interfaces import IIndexableWrapper
from Products.Zuul.infos.component.filesystem import FileSystemInfo as BaseFileSystemInfo

try:
    from Products.Zuul.catalog.global_catalog \
        import FileSystemWrapper as BaseFileSystemWrapper
except ImportError:
    # Zenoss 4.1 doesn't have FileSystemWrapper.
    from Products.Zuul.catalog.global_catalog import ComponentWrapper

    BaseFileSystemWrapper = ComponentWrapper

from Products.Zuul.interfaces.component import IFileSystemInfo as IBaseFileSystemInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
from ZenPacks.zenoss.LinuxMonitor.util import override_graph_labels, keyword_search


class FileSystem(BaseFileSystem):

    """Model class for FileSystem.

    Instances of this class get stored in ZODB.

    """

    class_label = "File System"
    plural_class_label = "File Systems"

    meta_type = 'LinuxFileSystem'

    server_name = None

    _properties = BaseFileSystem._properties + (
        {'id': 'server_name', 'label': 'Server Name', 'type': 'string'},
    )

    def logicalVolume(self):
        """Return the underlying LogicalVolume."""
        if not self.mount:
            return

        results = itertools.chain.from_iterable(
            self.device().search(name, mountpoint=self.mount)
            for name in ('LogicalVolume', 'SnapshotVolume'))

        for result in results:
            try:
                return result.getObject()
            except Exception:
                pass

    def blockDevice(self):
        """Return the underlying HardDisk."""
        if not self.mount:
            return

        device = self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            try:
                hd = brain.getObject()
            except Exception:
                continue
            else:
                if hd.mount == self.mount:
                    return hd

    def impacting_object(self):
        """Return the impacting LogicalVolume, HardDisk, or Device.

        A FileSystem can be impacted by only one of: it's underlying
        LogicalVolume, HardDisk, or Device. In that order.

        """
        lv = self.logicalVolume()
        if lv:
            return lv

        bd = self.blockDevice()
        if bd:
            return bd

        return self.device()

    @FunctionCache("LinuxFileSystem_getRRDTemplateName", default_timeout=60)
    def getRRDTemplateName(self):
        """
        Return name of monitoring template to bind to this component.

        Return non-existent template name if this FileSystem has external storage
        to prevent monitoring for such component on Linux device or
        returns the name of an appropriate template for this FileSystem otherwise.
        """
        storage_server = list(self.getStorageServer())
        if storage_server:
            return "FileSystem_NFS_Client"
        return "FileSystem"

    def getDefaultGraphDefs(self, drange=None):
        # Add and re-label graphs displayed in other components
        graphs = super(FileSystem, self).getDefaultGraphDefs(drange)

        bd = self.logicalVolume() or self.blockDevice()
        if bd:
            bdGraphs = override_graph_labels(bd, drange)
            graphs.extend(bdGraphs)

        return graphs

    def getGraphObjects(self):
        graphs = super(FileSystem, self).getGraphObjects()
        underlying = self.logicalVolume() or self.blockDevice()
        if underlying:
            for graph in underlying.getGraphObjects():
                graphs.append(graph)
        return graphs

    def getIconPath(self):
        '''
        Return the path to an icon for this component.
        '''
        return '/++resource++linux/img/file-system.png'

    def getStorageServer(self):
        """Generate objects for storage server for this FileSystem."""
        device = self.device()
        search_root = self.getDmdRoot('Devices').Storage

        try:
            for filesystem in getStorageServerPaths(device, search_root):
                filesystem = self.getObjByPath(filesystem)
                if self.storageDevice in filesystem.storage_clients_list:
                    yield filesystem
        except (AttributeError, NotFound,):
            """
            Pass if filesystem has been already deleted (NotFound)
            or if it is not a LinuxFileSystem instance (AttributeError).
            """


@FunctionCache("LinuxFileSystem_getStorageServerPaths", default_timeout=60)
def getStorageServerPaths(device, search_root):
    """Return the list of paths to external file system servers."""
    filesystem_servers = []
    search_keywords = set()
    for fs in device.os.filesystems():
        storage_device = fs.storageDevice
        if ':' in storage_device:
            search_keywords.add('has-nfs-client:{}'.format(storage_device))

    if search_keywords:
        for obj in keyword_search(search_root, search_keywords):
            filesystem_servers.append(obj.getPrimaryUrlPath())

    return filesystem_servers


class IFileSystemInfo(IBaseFileSystemInfo):

    """IInfo interface for FileSystem.

    This is used for JSON API definition. Fields described here are what will
    appear on instance's component details panel.

    """

    logicalVolume = schema.Entity(
        title=_t(u"LVM Logical Volume"),
        group="Details",
        readonly=True)

    blockDevice = schema.Entity(
        title=_t(u"Block Device"),
        group="Details",
        readonly=True)


class FileSystemInfo(BaseFileSystemInfo):

    """Info adapter for FileSystem.

    This is used for API implementation and JSON serialization. Properties
    implemented here will be available through the JSON API.

    """

    implements(IFileSystemInfo)

    server_name = ProxyProperty('server_name')

    @property
    @info
    def logicalVolume(self):
        return self._object.logicalVolume()

    @property
    @info
    def blockDevice(self):
        return self._object.blockDevice()

    @property
    @info
    def storageDevice(self):
        storage = self._object.storageDevice
        server_name = self._object.server_name
        if server_name:
            try:
                storage = ':'.join(
                    [server_name, storage.rsplit(':', 1)[1]]
                )
            except:
                pass
        for server in self._object.getStorageServer():
            return"<a class='z-entity' href='{0}'>{1}</a>".format(
                server.getPrimaryUrlPath(), storage)
        if self._object.logicalVolume():
            storagedevice = self._object.logicalVolume()
        elif self._object.blockDevice():
            storagedevice = self._object.blockDevice()
        else:
            return storage
        return"<a class='z-entity' href='{0}'>{1}</a>".format(
            storagedevice.getPrimaryUrlPath(), storagedevice.title)


class FileSystemWrapper(BaseFileSystemWrapper):
    '''
    Indexing adapter for FileSystem.
    '''

    implements(IIndexableWrapper)
    adapts(FileSystem)

    def searchKeywordsForChildren(self):
        """Return tuple of search keywords for FileSystem objects.

        Overrides ComponentWrapper to add junction point information for the FileSystem.
        This provides a way for storage servers to find
        the Linux FileSystem components by their junction point.

        """
        keywords = set()

        storage_device = self._context.storageDevice
        if ':' in storage_device:
            keywords.add(
                'has-nfs-server:{0}'.format(
                    storage_device
                )
            )

        return (
            super(FileSystemWrapper, self).searchKeywordsForChildren() +
            tuple(keywords))
