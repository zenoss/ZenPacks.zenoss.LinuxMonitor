##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

# logging
import logging

# Zenoss Imports
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration

log = logging.getLogger('zen.LinuxMonitor')


class EditDefaultzLinuxServicesModeled(ZenPackMigration):
    version = Version(2, 3, 1)

    def migrate(self, pack):
        org = pack.dmd.Devices.Server.SSH.Linux
        if getattr(org, 'zLinuxServicesModeled', None) == ['.*']:
            org.setZenProperty('zLinuxServicesModeled', [])
