##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
LOG = logging.getLogger("zen.LinuxMonitor")

from ZenPacks.zenoss.ZenPackLib import zenpacklib
import os.path
from Products.CMFCore.DirectoryView import registerDirectory

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

# CFG is necessary when using zenpacklib.TestCase.
CFG = zenpacklib.load_yaml()

schema = CFG.zenpack_module.schema
from . import transforms


class ZenPack(schema.ZenPack):
    """ZenPack class override"""
    packZProperties_data = {
        'zLinuxServicesModeled': {
            'type': 'lines',
            'description': 'Sets regular expressions of services to model',
            'label': 'Linux Services Modeled'},
        'zLinuxServicesNotModeled': {
            'type': 'lines',
            'description': 'Sets regular expressions of services to not model',
            'label': 'Linux Services Not Modeled'},
    }

    def install(self, app):
        super(ZenPack, self).install(app)

        self.register_devtype(
            app.zport.dmd,
            deviceclass="/Server/SSH/Linux",
            description="Linux Server",
            protocol="SSH")
        try:
            self.dmd.ZenPackManager.packs._getOb(
                'ZenPacks.zenoss.EnterpriseLinux')
            LOG.info(' '.join(["EnterpriseLinux ZenPack is not required",
                               "for the LinuxMonitor ZenPack"]))
        except AttributeError:
            pass

        transforms.install_transforms(app.zport.dmd)

    def register_devtype(self, dmd, deviceclass, description, protocol):
        try:
            deviceclass = dmd.Devices.getOrganizer(deviceclass)

            if (description, protocol) not in deviceclass.devtypes:
                LOG.info(
                    "registering %s (%s) device type",
                    description,
                    protocol)

                deviceclass.register_devtype(description, protocol)
        except Exception:
            pass


# Patch last to avoid import recursion problems.
from ZenPacks.zenoss.LinuxMonitor import patches  # NOQA
