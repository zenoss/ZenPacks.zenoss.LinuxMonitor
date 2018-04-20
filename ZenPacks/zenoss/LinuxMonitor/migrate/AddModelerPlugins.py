##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
ZPL 2.0 does not overwrite existing zProperties for a device class
"""
# logging
import logging

# Zenoss Imports
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration

log = logging.getLogger('zen.LinuxMonitor')


class AddModelerPlugins(ZenPackMigration):
    version = Version(2, 3, 0)

    def migrate(self, pack):
        new_plugins = [  'zenoss.cmd.linux.interfaces',
                         'zenoss.cmd.linux.lvm',
                         'zenoss.cmd.linux.sudo_dmidecode',
                         'zenoss.cmd.linux.os_release',
                         'zenoss.cmd.linux.os_service']

        old_plugins = [  'zenoss.cmd.linux.alt_kernel_name',
                         'zenoss.cmd.linux.rpm']

        changed = False
        dcObject = pack.dmd.Devices.getOrganizer('/Server/SSH/Linux')
        zCollectorPlugins = dcObject.zCollectorPlugins
        for new_plugin in new_plugins:
            if new_plugin not in zCollectorPlugins:
                log.debug('Adding {} modeler plugin to zCollectorPlugins for'
                          ' /Server/SSH/Linux'.format(new_plugin))
                zCollectorPlugins.append(new_plugin)
                changed = True

        for old_plugin in old_plugins:
            if old_plugin in zCollectorPlugins:
                log.debug('Removing {} modeler plugin from zCollectorPlugins for'
                          ' /Server/SSH/Linux'.format(old_plugin))
                zCollectorPlugins.remove(old_plugin)
                changed = True


        if changed:
            dcObject.setZenProperty('zCollectorPlugins', zCollectorPlugins)
            # apply also to any sub-device classes or devices with locally defined plugins
            for ob in dcObject.getOverriddenObjects("zCollectorPlugins", showDevices=True):
                collector_plugins = ob.zCollectorPlugins
                for new_plugin in new_plugins:
                    if new_plugin not in collector_plugins:
                        log.debug('Adding {} modeler plugin to zCollectorPlugins for {}'
                                    .format(new_plugin,ob.getDmdKey()))
                        collector_plugins.append(new_plugin)
                for old_plugin in old_plugins:
                    if old_plugin in collector_plugins:
                        log.debug('Removing {} modeler plugin from zCollectorPlugins for {}'
                                    .format(old_plugin,ob.getDmdKey()))
                        collector_plugins.remove(old_plugin)
                ob.setZenProperty('zCollectorPlugins', collector_plugins)
