###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################


import os

from Products.ZenRRD.tests.BaseParsersTestCase import BaseParsersTestCase
from Products.ZenRRD.parsers.uptime import uptime

from ZenPacks.zenoss.LinuxMonitor.parsers.linux.df import df
from ZenPacks.zenoss.LinuxMonitor.parsers.linux.dfi import dfi
from ZenPacks.zenoss.LinuxMonitor.parsers.linux.ifconfig import ifconfig
from ZenPacks.zenoss.LinuxMonitor.parsers.linux.free import free
from ZenPacks.zenoss.LinuxMonitor.parsers.linux.diskstats import diskstats


class LinuxParsersTestCase(BaseParsersTestCase):

    def testLinuxParsers(self):
        """
        Test all of the parsers that have test data files in the data
        directory.
        """
        datadir = "%s/parserdata/linux" % os.path.dirname(__file__)
        
        parserMap = {'/bin/df -Pk': df,
                     '/bin/df -iPk': dfi,
                     '/sbin/ifconfig -a': ifconfig,
                     '/usr/bin/free': free,
                     '/usr/bin/uptime': uptime,
                     '/bin/cat /proc/diskstats': diskstats,
                     }
        
        self._testParsers(datadir, parserMap)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(LinuxParsersTestCase))
    return suite

