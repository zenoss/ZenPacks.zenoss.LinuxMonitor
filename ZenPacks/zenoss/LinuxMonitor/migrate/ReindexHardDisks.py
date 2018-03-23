##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging

from zope.event import notify
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version
from Products.Zuul.interfaces import ICatalogTool
from Products.Zuul.catalog.events import IndexingEvent

from ZenPacks.zenoss.LinuxMonitor.HardDisk import HardDisk
from ZenPacks.zenoss.LinuxMonitor.FileSystem import FileSystem

log = logging.getLogger("zen.migrate")

__doc__ = """
Reindex HardDisk and FileSystem components to add keyword search indexes and update IndexableWrapper
"""


class ReindexHardDisks(ZenPackMigration):
    """
    Update searchKeywords index for existing HardDisk and FileSystem components
    """
    version = Version(2, 3, 0)

    def migrate(self, pack):
        hd_fs_brains = ICatalogTool(pack.dmd.Devices).search(
            [FileSystem, HardDisk]
        )
        for result in hd_fs_brains:
            try:
                notify(IndexingEvent(result.getObject()))
            except Exception:
                continue
