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

import logging
log = logging.getLogger("zen.migrate")

def getSshLinux(dmd):
    ssh = None
    sshLinux = None
    if dmd.Devices.Server.hasObject('SSH'):
        ssh = dmd.Devices.Server.SSH
    if ssh and ssh.hasObject('Linux'):
        sshLinux = ssh.Linux
    return sshLinux

class FixProcessCpuAxisLabel(ZenPackMigration):
    version = Version(1, 3, 3)

    def migrate(self, pack):
        try:
            sshLinux = getSshLinux(pack.dmd)
            if sshLinux:
                graphDef = sshLinux.rrdTemplates.OSProcess.graphDefs._getOb('process performance')
                graphDef.units = 'percentage'
        except Exception, e:
            log.debug('Exception trying to modify process performance '
                      'graph axis label')


FixProcessCpuAxisLabel()
