###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import os

from Products.DataCollector.tests.BasePluginsTestCase import BasePluginsTestCase

from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.ifconfig import ifconfig

class LinuxPluginsTestCase(BasePluginsTestCase):
    
    
    def runTest(self):
        """
        Test all of the plugins that have test data files in the data
        directory.
        """
        
        Plugins = [ifconfig,]
        
        datadir = "%s/plugindata/linux" % (os.path.dirname(__file__))
        self._testDataFiles(datadir, Plugins)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(LinuxPluginsTestCase))
    return suite
