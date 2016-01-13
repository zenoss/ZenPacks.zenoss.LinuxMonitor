##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
import os

from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

log = logging.getLogger("zen.migrate")

__doc__ = """
Rename Enterprise modeler plugins and parsers
"""


class renameEnterprisePlugins(ZenPackMigration):
    """
    """
    version = Version(2, 0, 0)

    def migrate(self, pack):
        try:
            z = pack.dmd.ZenPackManager.packs._getOb('ZenPacks.zenoss.EnterpriseLinux')
        except AttributeError:
            return
        log.info('Deprecating EnterpriseLinux plugins and parsers.')
        zpath = os.path.join(z.path(), 'modeler/plugins/zenoss/cmd/linux')
        for filename in ('alt_kernel_name', 'rpm', 'sudo_dmidecode'):
            self.renameFile(zpath, filename)
        zpath = os.path.join(z.path(), 'parsers/linux')
        for filename in ('diskstats', 'ifconfig'):
            self.renameFile(zpath, filename)

    def renameFile(self, zpath, filename):
        if not zpath or not filename:
            return
        if os.path.exists(os.path.join(zpath, filename+'.py')):
            os.rename(os.path.join(zpath, filename+'.py'), os.path.join(zpath, filename+'_deprecated.py'))
