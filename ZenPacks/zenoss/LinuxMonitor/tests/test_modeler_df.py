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
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.df import df

# Ubuntu 16.04.2 LTS
# Linux puffer 4.4.0-72-generic #93-Ubuntu SMP Fri Mar 31 14:07:41 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
EXAMPLE_OUTPUT = """
Filesystem                                              Type     1024-blocks     Used Available Capacity Mounted on
udev                                                    devtmpfs    32907768        0  32907768       0% /dev
tmpfs                                                   tmpfs        6585696    70236   6515460       2% /run
/dev/sda7                                               ext4        19554584  7314944  11223272      40% /
tmpfs                                                   tmpfs       32928468      268  32928200       1% /dev/shm
tmpfs                                                   tmpfs           5120        4      5116       1% /run/lock
tmpfs                                                   tmpfs       32928468        0  32928468       0% /sys/fs/cgroup
/dev/sda6                                               ext4          475754   410016     36657      92% /boot
/dev/mapper/data-z                                      ext4        61796348 18697752  39936484      32% /z
/dev/mapper/data-home                                   ext4        20511356  1794480  17651916      10% /home
/dev/sda1                                               vfat          507904    47176    460728      10% /boot/efi
tmpfs                                                   tmpfs        6585696       64   6585632       1% /run/user/1000
tmpfs                                                   tmpfs        6585696        0   6585696       0% /run/user/1337
/dev/mapper/docker-252:1-3676969-2vtb4DkSxaGhsEG28N5Gty xfs        104805376  2421208 102384168       3% /exports/serviced_volumes_v2/bgxogiyx1b2gc94i1wh2lm2c2
192.168.2.2:/exports/serviced_volumes_v2                nfs         19555328  7315456  11224064      40% /mnt/test
"""


LOG = logging.getLogger("zen.testcases")


class FileSystemModelerTests(unittest.TestCase):

    def setUp(self):
        super(FileSystemModelerTests, self).setUp()

        self.plugin = df()
        self.device = DeviceProxy()
        self.device.id = "test-FileSystemModeler"
        self.device.zFileSystemSizeOffset = 1.0
        self.device.zFileSystemMapIgnoreNames = ""
        self.device.zFileSystemMapIgnoreTypes = []

        # self.deviceclass = self.dmd.Devices.createOrganizer("/Server/SSH/Linux")
        # self.deviceclass.setZenProperty(
        #     "zPythonClass",
        #     "ZenPacks.zenoss.LinuxMonitor.LinuxDevice")
        #
        # self.deviceclass.setZenProperty(
        #     "zFileSystemMapIgnoreTypes", [
        #         "other",
        #         "ram",
        #         "virtualMemory",
        #         "removableDisk",
        #         "floppyDisk",
        #         "compactDisk",
        #         "ramDisk",
        #         "flashMemory",
        #         "networkDisk"])
        #
        # self.device = self.deviceclass.createInstance("test-FileSystemModeler")

    def test_zFileSystemMapIgnoreNames(self):
        # Test with the default value of zFileSystemIgnoreNames.
        self.device.zFileSystemMapIgnoreNames = ""
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 14)

        # Test with a null value for zFileSystemIgnoreNames.
        self.device.zFileSystemMapIgnoreNames = None
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 14)

        # Test with zFileSystemIgnoreNames set to a single-matching regex.
        self.device.zFileSystemMapIgnoreNames = "^/boot$"
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 13)

        # Test with zFileSystemIgnoreNames set to a multi-maching regex.
        self.device.zFileSystemMapIgnoreNames = "^/run/"
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 11)

    def test_zFileSystemMapIgnoreTypes(self):
        # Test the default value of zFileSystemIgnoreTypes.
        self.device.zFileSystemMapIgnoreTypes = [
            "other",
            "ram",
            "virtualMemory",
            "removableDisk",
            "floppyDisk",
            "compactDisk",
            "ramDisk",
            "flashMemory",
            "networkDisk"]

        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 14)

        # Test a null value for zFileSystemMapIgnoreTypes.
        self.device.zFileSystemMapIgnoreTypes = None
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 14)

        # Test an empty list for zFileSystemIgnoreTypes.
        self.device.zFileSystemMapIgnoreTypes = []
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 14)

        # Test with zFileSystemIgnoreTypes ignoring one filesystem by type.
        self.device.zFileSystemMapIgnoreTypes = ["nfs"]
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 13)

        # Test with zFileSystemIgnoreTypes set to a list of regexes.
        self.device.zFileSystemMapIgnoreTypes = ["tmpfs", "xfs"]
        rm = self.plugin.process(self.device, EXAMPLE_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 6)
