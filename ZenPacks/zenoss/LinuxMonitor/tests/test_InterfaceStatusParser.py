##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import unittest

from ZenPacks.zenoss.LinuxMonitor.parsers.linux.ifconfig import ifconfig, AltScanConfig

from Products.ZenRRD.CommandParser import ParsedResults

EXAMPLE_OUTPUT = """1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT \n    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n    RX: bytes  packets  errors  dropped overrun mcast   \n    3320       39       0       0       0       0      \n    TX: bytes  packets  errors  dropped carrier collsns \n    3320       39       0       0       0       0      
2: eth0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 9001 qdisc pfifo_fast state UP mode DEFAULT qlen 1000\n    link/ether 12:af:53:48:18:04 brd ff:ff:ff:ff:ff:ff\n    RX: bytes  packets  errors  dropped overrun mcast   \n    274586     3129     0       0       0       0      \n    TX: bytes  packets  errors  dropped carrier collsns \n    749443     2919     0       0       0       0      
"""


class InterfaceStatusParser(unittest.TestCase):

    def setUp(self):
        super(InterfaceStatusParser, self).setUp()

        dp1 = type('test_dp1', (object,), {})
        dp1.data = {'componentScanValue': 'eth0'}
        dp1.id = 'ifAdminStatus'

        dp2 = type('test_dp2', (object,), {})
        dp2.data = {'componentScanValue': 'eth0'}
        dp2.id = 'ifOperStatus'

        self.cmd = type('test_cmd', (object,), {})
        self.cmd.component = 'eth0'
        self.cmd.points = [dp1, dp2]
        self.cmd.result = type('test_result', (object,), {})
        self.cmd.result.output = EXAMPLE_OUTPUT

    def test_InterfaceStatusParser(self):
        """Test parsing statuses through find_status method."""
        res = ParsedResults()
        ifconfig_obj = ifconfig()
        ifconfig_obj.componentSplit = AltScanConfig.componentSplit
        ifconfig_obj.componentScanner = AltScanConfig.componentScanner
        values = ifconfig_obj.find_status(self.cmd, res).values
        self.assertEqual((values[0][0].component, values[0][0].id, values[0][1]), ('eth0', 'ifAdminStatus', 2.0))
        self.assertEqual((values[1][0].component, values[1][0].id, values[1][1]), ('eth0', 'ifOperStatus', 1.0))
