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

class ChangePsTemplateTargetPythonClass(ZenPackMigration):
    """
    targetPythonClass of /zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/OSProcess
    was incorrectly set to Device instead of OSProcess.
    """

    version = Version(1, 3, 2)

    def migrate(self, pack):
        try:
            path = '/zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/OSProcess'
            template = pack.dmd.unrestrictedTraverse(path)
        except Exception:
            log.debug('Unable to find OSProcess template')
        else:
            targetPythonClass = getattr(template, 'targetPythonClass', None)
            if targetPythonClass != 'Products.ZenModel.OSProcess':
                log.info('Fixing targetPythonClass on OSProcess template')
                template.targetPythonClass = 'Products.ZenModel.OSProcess'

ChangePsTemplateTargetPythonClass()
