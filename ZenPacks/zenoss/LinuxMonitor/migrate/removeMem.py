##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2011, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


__doc__ = """
 Remove memory graph that doesn't improve the base graphs.

https://dev.zenoss.com/tracint/ticket/2853
"""

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

class removeMem( ZenPackMigration ):
    """The Memory Utilization graphdef is replaced by the Free Memory and Free
    Swap graphs in the LinuxMonitor zenpack.
    """
    version = Version(1, 2, 0)

    def migrate(self, pack):
        try:
            log.info( 'remove memory utilization graph')
            sshLinux = getSshLinux(pack.dmd)
            if sshLinux:
                device_template = sshLinux.rrdTemplates.Device
                device_template.graphDefs._delObject('Memory Utilization')
        except Exception, e:
            log.debug('Failed to delete memory utilization graph (%s: %s)' % (type(e).__name__, e))


removeMem()
