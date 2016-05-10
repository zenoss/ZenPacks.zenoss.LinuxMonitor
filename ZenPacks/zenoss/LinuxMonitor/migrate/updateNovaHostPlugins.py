##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

log = logging.getLogger("zen.migrate")

__doc__ = """
Update plugins for NovaHost organizer from ZP OSI
"""


class updateNovaHostPlugins(ZenPackMigration):
    """
    """
    version = Version(2, 0, 0)

    def migrate(self, pack):
        try:
            from ZenPacks.zenoss.OpenStackInfrastructure import NOVAHOST_PLUGINS
            log.info('Updating plugins for NovaHost organizer')
            novahost = pack.dmd.Devices.getOrganizer('/Server/SSH/Linux/NovaHost')
            dc = pack.dmd.Devices.getOrganizer('/Server/SSH/Linux')
            linux_plugins = dc.zCollectorPlugins
            novahost.zCollectorPlugins = linux_plugins + NOVAHOST_PLUGINS
        except ImportError:
            pass
