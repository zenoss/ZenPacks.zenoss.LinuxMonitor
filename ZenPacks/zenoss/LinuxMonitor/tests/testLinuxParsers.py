##########################################################################
#
#   Copyright 2009 Zenoss, Inc. All Rights Reserved.
#
##########################################################################


import os

from Products.ZenRRD.tests.BaseParsersTestCase import BaseParsersTestCase
from Products.ZenRRD.parsers.uptime import uptime

from ZenPacks.zenoss.LinuxMonitor.parsers.linux.df import df
from ZenPacks.zenoss.LinuxMonitor.parsers.linux.dfi import dfi

class LinuxParsersTestCase(BaseParsersTestCase):

    def testLinuxParsers(self):
        """
        Test all of the parsers that have test data files in the data
        directory.
        """
        datadir = "%s/parserdata/linux" % os.path.dirname(__file__)
        
        parserMap = {'/bin/df -Pk': df,
                     '/bin/df -iPk': dfi,
                     '/usr/bin/uptime': uptime,
                     }
        
        self._testParsers(datadir, parserMap)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(LinuxParsersTestCase))
    return suite

