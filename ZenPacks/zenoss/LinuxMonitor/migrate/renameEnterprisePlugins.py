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
        for z in pack.dmd.ZenPackManager.packs():
            if 'ZenPacks.zenoss.EnterpriseLinux' == z.id:
                zpath = os.path.join(z.path(), 'modeler/plugins/zenoss/cmd/linux')
                self.renameFile(zpath, 'alt_kernel_name')
                self.renameFile(zpath, 'rpm')
                self.renameFile(zpath, 'sudo_dmidecode')
                zpath = os.path.join(z.path(), 'parsers/linux')
                self.renameFile(zpath, 'diskstats')
                self.renameFile(zpath, 'ifconfig')
                break

    def renameFile(self, zpath, filename):
        if not zpath or not filename:
            return
        if os.path.exists(os.path.join(zpath, filename+'.py')):
            os.rename(os.path.join(zpath, filename, '.py'), os.path.join(zpath, filename+'_deprecated.py'))
