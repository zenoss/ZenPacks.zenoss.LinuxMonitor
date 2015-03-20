##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import Globals
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

import logging
log = logging.getLogger("zen.migrate")

def getSshLinux( dmd ):
    ssh = None
    sshLinux = None
    if dmd.Devices.Server.hasObject('SSH'):
        ssh = dmd.Devices.Server.SSH
    if ssh and ssh.hasObject('Linux'):
        sshLinux = ssh.Linux
    return sshLinux

class RemoveCpuAlias( ZenPackMigration ):
    """
    We are removing the cpu__pct alias on ssCpuIdle since it is now on ssCpuIdlePerCpu instead
    """

    version = Version(1, 3, 0)

    def migrate(self, pack):
        try:
            log.info( 'Removing ssCpuIdle cpu__pct alias if necessary')
            sshLinux = getSshLinux( pack.dmd )
            if sshLinux:
                deviceTemplate = sshLinux.rrdTemplates.Device
                # Get the ssCpuIdle datapoint
                cpuIdleDp = deviceTemplate.datasources.cpu.datapoints.ssCpuIdle
                # If it has a cpu__pct alias, delete it
                if cpuIdleDp.hasAlias( 'cpu__pct' ):
                    cpuIdleDp.aliases._delObject('cpu__pct')
        except Exception, e:
            log.debug( 'Exception trying to remove cpu__pct alias from ssCpuIdle' )


RemoveCpuAlias()
