##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import Globals
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenUtils.Utils import unused
unused(Globals)

import logging
log = logging.getLogger("zen.migrate")

def getSshLinux(dmd):
    try:
        return dmd.Devices.Server.SSH.Linux
    except Exception:
        return None

class changeIOUnits( ZenPackMigration ):
    """
    Units on the IO graph displayed bytes/sec but the
    graphs value is sectors/sec.
    """

    version = Version(1, 3, 1)

    def migrate(self, pack):
        try:
            log.info("Changing IO graph unit from bytes/sec to sectors/sec.")
            sshLinux = getSshLinux(pack.dmd)
            if sshLinux:
                IOgraph = sshLinux.rrdTemplates.Device.graphDefs.IO
                log.debug("Current IO graph value is %r", IOgraph.units)
                IOgraph.units = 'blocks/sec'

        except Exception as ex:
            log.debug( 'Exception changing IO graph units from bytes/sec to sectors/sec.' )
            log.exception(ex)


changeIOUnits()
