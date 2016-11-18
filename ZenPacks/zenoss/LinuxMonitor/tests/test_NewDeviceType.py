##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Test cases for NewDeviceType migration."""

import datetime

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused

unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from Products.DataCollector.plugins.DataMaps import RelationshipMap
from Products.ZenModel.Device import Device

from ZenPacks.zenoss.LinuxMonitor import ZenPack
from ZenPacks.zenoss.LinuxMonitor.LinuxDevice import LinuxDevice
from ZenPacks.zenoss.LinuxMonitor.migrate.NewDeviceType import NewDeviceType

from ZenPacks.zenoss.LinuxMonitor.tests.utils import create_device
from ZenPacks.zenoss.LinuxMonitor.tests.test_dvi import DATAMAPS as NEW_DATAMAPS


OLD_DATAMAPS = [
    RelationshipMap(
        modname="Products.ZenModel.FileSystem",
        compname="os",
        relname="filesystems",
        objmaps=[{"id": "data{}".format(i)} for i in range(100)]),

    RelationshipMap(
        modname="Products.ZenModel.IpInterface",
        compname="os",
        relname="interfaces",
        objmaps=[{"id": "eth{}".format(i)} for i in range(100)]),

    RelationshipMap(
        modname="Products.ZenModel.CPU",
        compname="hw",
        relname="cpus",
        objmaps=[{"id": "cpu{}".format(i)} for i in range(100)]),

    RelationshipMap(
        modname="Products.ZenModel.HardDisk",
        compname="hw",
        relname="harddisks",
        objmaps=[{"id": "hda{}".format(i)} for i in range(100)]),
]


class migrateTests(BaseTestCase):
    """Tests for NewDeviceType.migrate."""

    def afterSetUp(self):
        """Setup for tests in this TestCase."""
        super(migrateTests, self).afterSetUp()

        pack = ZenPack("ZenPacks.zenoss.LinuxMonitor")
        packs = self.dmd.ZenPackManager.packs
        packs._setObject(pack.id, pack)
        self.pack = packs._getOb(pack.id)
        self.step = NewDeviceType()

        # OpenStack integration assumes /OpenStack/Infrastructure device class.
        self.dmd.Devices.createOrganizer("/OpenStack/Infrastructure")

    def test_one_device(self):
        """Test migration of one device.

        This test is to verify that the device is migrated correctly.
        See test_ten_devices for migration performance testing.

        """
        device = create_device(
            self.dmd,
            "Products.ZenModel.Device",
            "test-linux1",
            OLD_DATAMAPS)

        self.assertTrue(
            device.__class__ == Device,
            "{} is a {!r} instead of a {!r}".format(
                device.id,
                device.__class__,
                Device))

        self.assertTrue(
            len(device.getDeviceComponents()) == 400,
            "{} has {} components instead of {}".format(
                device.id,
                len(device.getDeviceComponents()),
                400))

        self.step.migrate(self.pack)

        device = create_device(
            self.dmd,
            "ZenPacks.zenoss.LinuxMonitor.LinuxDevice",
            "test-linux1",
            NEW_DATAMAPS)

        self.assertTrue(
            device.__class__ == LinuxDevice,
            "{} is a {!r} instead of a {!r}".format(
                device.id,
                device.__class__,
                Device))

        self.assertTrue(
            len(device.getDeviceComponents()) == 30,
            "{} has {} components instead of {}".format(
                device.id,
                len(device.getDeviceComponents()),
                30))

    def test_ten_devices(self):
        """Test migration of ten devices.

        This test is here to test migration performance. See
        test_one_device for a test of correct migration.

        Using device.changeDeviceClass in the NewDeviceType migrate step
        resulted in this test taking 212.98 seconds (21.30 seconds per
        device) on my development system. After switching NewDeviceType
        to change device.__class__ instead of changeDeviceClass, it took
        0.02 seconds (0.002 seconds per device). The test devices have
        400 components.

        """
        count = 10

        for i in range(count):
            create_device(
                self.dmd,
                "Products.ZenModel.Device",
                "test-linux{}".format(i),
                OLD_DATAMAPS)

        start = datetime.datetime.now()
        self.step.migrate(self.pack)
        duration = datetime.datetime.now() - start

        self.assertTrue(
            duration.total_seconds() < count / 10.0,
            "{} devices took to long to migrate ({})".format(
                count,
                duration))

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(migrateTests))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
