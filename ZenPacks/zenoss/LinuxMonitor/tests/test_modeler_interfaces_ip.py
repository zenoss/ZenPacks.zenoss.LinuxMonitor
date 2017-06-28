##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import Globals  # noqa - imported for side effects

import logging
import unittest

from Products.DataCollector.DeviceProxy import DeviceProxy
# from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.interfaces import interfaces

# Test the interfaces.parseIpconfig that process 'ip address' output from iproute
# Warning: DO not remove whitespace from EXAMPLE_OUTPUT, it is required!

EXAMPLE_OUTPUT = """
### ip address output
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc pfifo_fast state UP qlen 1000
    link/ether 12:ac:cf:e4:f3:64 brd ff:ff:ff:ff:ff:ff
    inet 10.111.5.200/24 brd 10.111.5.255 scope global dynamic eth0
       valid_lft 3110sec preferred_lft 3110sec
    inet 192.168.222.8/24 brd 192.168.222.255 scope global eth0:1
       valid_lft forever preferred_lft forever
    inet6 2002:c000:203::1111/16 scope global deprecated 
       valid_lft forever preferred_lft 0sec
    inet6 fe80::10ac:cfff:fee4:f364/64 scope link 
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:1f:5b:36:21:89 brd ff:ff:ff:ff:ff:ff
4: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
    link/ether 00:1f:5b:36:21:88 brd ff:ff:ff:ff:ff:ff
    inet 10.30.1.50/24 brd 10.30.1.255 scope global br0
       valid_lft forever preferred_lft forever 
5: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 100
    link/none
    inet 10.0.9.6 peer 10.0.9.5/32 scope global tun0
       valid_lft forever preferred_lft forever 
6: wlan0: <BROADCAST,MULTICAST> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 6c:88:14:8d:6d:e0 brd ff:ff:ff:ff:ff:ff
7: virbr0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
    link/ether fe:54:00:1e:21:d2 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0
       valid_lft forever preferred_lft forever
8: vnet0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master virbr0 state UNKNOWN group default qlen 500
    link/ether fe:54:00:1e:21:d2 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::fc54:ff:fe1e:21d2/64 scope link 
       valid_lft forever preferred_lft forever
9: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue state UP
    link/ether 02:42:1d:d7:33:ca brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/24 scope global docker0
       valid_lft forever preferred_lft forever
10: vethdc72075: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 9e:23:77:e8:c1:4b brd ff:ff:ff:ff:ff:ff
11: veth4668200: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 7e:36:bb:fb:22:cc brd ff:ff:ff:ff:ff:ff
12: vnet0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master br0 state UNKNOWN group default qlen 500
    link/ether fe:54:00:6a:b0:2e brd ff:ff:ff:ff:ff:ff
13: vethd24adb7: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 42:42:ac:79:da:90 brd ff:ff:ff:ff:ff:ff
14: veth2ce8778: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether ee:e9:27:5e:02:ee brd ff:ff:ff:ff:ff:ff
15: veth9a6c7ea: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 6e:6a:69:0b:a9:18 brd ff:ff:ff:ff:ff:ff
16: vethd3cdf9d: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether be:a3:e2:d7:5c:e5 brd ff:ff:ff:ff:ff:ff
17: vethcb4f309: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether fa:eb:8f:f0:3a:1e brd ff:ff:ff:ff:ff:ff
18: veth5c1e50b: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 6a:e5:c0:c1:78:8d brd ff:ff:ff:ff:ff:ff
19: vethebc7542: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 82:27:97:56:8e:d9 brd ff:ff:ff:ff:ff:ff
20: vethfecb1c0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 22:a9:43:e6:e1:9f brd ff:ff:ff:ff:ff:ff
21: veth6c25364: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether a6:b7:39:4c:1d:a0 brd ff:ff:ff:ff:ff:ff
22: veth8875938: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 8e:8e:4b:84:65:27 brd ff:ff:ff:ff:ff:ff
23: veth68a7d7c: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether a2:ad:75:62:83:16 brd ff:ff:ff:ff:ff:ff
24: veth93c58ab: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 1e:f9:c3:25:9e:2c brd ff:ff:ff:ff:ff:ff
25: vethf22fd2e: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 3e:8e:28:67:b9:1c brd ff:ff:ff:ff:ff:ff
26: veth0d6ee1f: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether be:0f:79:6c:f9:87 brd ff:ff:ff:ff:ff:ff
27: veth0dd1855: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether a2:d3:2d:b4:54:4a brd ff:ff:ff:ff:ff:ff
28: vethb01fdd9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 36:50:ee:c3:26:1c brd ff:ff:ff:ff:ff:ff
29: vethb81a853: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 8e:6f:e9:55:6e:11 brd ff:ff:ff:ff:ff:ff
30: vetha24d78c: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether da:5e:b5:1e:8d:08 brd ff:ff:ff:ff:ff:ff
31: vetha51db47: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 42:ad:8f:9d:5a:a2 brd ff:ff:ff:ff:ff:ff
32: vethd1933ee: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 62:66:21:03:dd:00 brd ff:ff:ff:ff:ff:ff
33: veth7bf4901: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether ea:76:f4:6f:a6:f8 brd ff:ff:ff:ff:ff:ff
34: veth324a276: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 8a:7b:b0:bf:88:be brd ff:ff:ff:ff:ff:ff
35: veth1b8bb37: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 9e:17:0e:89:99:5f brd ff:ff:ff:ff:ff:ff
36: vethe666bd3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether ae:aa:67:50:61:82 brd ff:ff:ff:ff:ff:ff
37: veth2900238: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 6e:22:c2:7d:8c:52 brd ff:ff:ff:ff:ff:ff
38: veth4ba46d4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 32:42:aa:99:07:9d brd ff:ff:ff:ff:ff:ff
39: veth3cb15ed: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP 
    link/ether 96:9a:24:fc:06:57 brd ff:ff:ff:ff:ff:ff
40: veth73054c3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 500 qdisc noqueue master docker0 state UP  
    link/ether f2:76:1e:cb:db:bb brd ff:ff:ff:ff:ff:ff
__COMMAND__
nothing
__COMMAND__
nothing
"""

LOG = logging.getLogger("zen.testcases")


class InterfaceModelerTests(unittest.TestCase):

    def setUp(self):
        super(InterfaceModelerTests, self).setUp()

        self.plugin = interfaces()
        self.device = DeviceProxy()
        self.device.id = "test-InterfacesIp"
        self.device.zInterfaceMapIgnoreNames = ""
        self.device.zInterfaceMapIgnoreTypes = ""

    def test_zInterfaceMapIgnoreNames(self):
        # Test with the default value of zInterfaceIgnoreNames.
        self.device.zInterfaceMapIgnoreNames = ""
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 40)

        # Test with a null value for zInterfaceIgnoreNames.
        self.device.zInterfaceMapIgnoreNames = None
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 40)

        # Test with zInterfaceIgnoreNames set to a single-matching regex.
        self.device.zInterfaceMapIgnoreNames = "docker0"
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 39)

    def test_zInterfaceMapIgnoreTypes(self):
        # Test the default value of zInterfaceIgnoreTypes.
        self.device.zInterfaceMapIgnoreTypes = ''
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 40)

        # Test a null value for zInterfaceMapIgnoreTypes.
        self.device.zInterfaceMapIgnoreTypes = None
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 40)

        # Test ethernetCsmacd for zInterfaceIgnoreTypes.
        self.device.zInterfaceMapIgnoreTypes = "ethernetCsmacd"
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm.maps), 2)
