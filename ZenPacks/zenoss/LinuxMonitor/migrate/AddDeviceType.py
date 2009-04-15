###########################################################################
#
# Copyright 2009 Zenoss, Inc. All Rights Reserved.
#
###########################################################################

from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration

import logging
log = logging.getLogger("zen.LinuxMonitor")

class AddDeviceType(ZenPackMigration):
    version = Version(2, 4, 0)

    def migrate(self, dmd):
        try:
            devclass = dmd.Devices.Server.SSH.Linux
        except AttributeError:
            # Something is horribly wrong, so stop trying
            pass
        else:
            devclass.register_devtype('Linux Server', 'SSH')

AddDeviceType()
