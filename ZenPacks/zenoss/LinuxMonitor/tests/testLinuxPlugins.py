##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


import os

from Products.DataCollector.tests.BasePluginsTestCase \
    import BasePluginsTestCase
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.alt_kernel_name import alt_kernel_name
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.cpuinfo import cpuinfo
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.lvm import lvm
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.rpm import rpm
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.sudo_dmidecode import sudo_dmidecode
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.\
    cmd.linux.df import df


class testPlugins(BasePluginsTestCase):

    def runTest(self):
        """
        Test all of the plugins that have test data files in the data
        directory.
        """
        Plugins = [cpuinfo, alt_kernel_name, sudo_dmidecode, lvm, df]
        datadir = "%s/plugindata/" % os.path.dirname(__file__)
        self._testDataFiles(datadir, Plugins)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPlugins))
    return suite
