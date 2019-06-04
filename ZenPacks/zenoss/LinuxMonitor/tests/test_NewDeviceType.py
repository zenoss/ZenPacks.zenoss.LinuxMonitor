##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016-2019, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Test cases for NewDeviceType migration."""

import datetime
import unittest

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenModel.Device import Device

from ZenPacks.zenoss.ZenPackLib import zenpacklib
from .. import ZenPack
from ..LinuxDevice import LinuxDevice
from ..migrate.NewDeviceType import NewDeviceType

zenpacklib.enableTesting()


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

NEW_DATAMAPS = [
    RelationshipMap(
        modname="Products.ZenModel.CPU",
        compname="hw",
        relname="cpus",
        objmaps=[
            ObjectMap({"id": "0"}),
            ObjectMap({"id": "1"}),
            ]),

    RelationshipMap(
        modname="Products.ZenModel.OSProcess",
        compname="os",
        relname="processes",
        objmaps=[
            ObjectMap({"id": "docker"}),
            ObjectMap({"id": "memcached"}),
            ]),

    RelationshipMap(
        modname="Products.ZenModel.IpService",
        compname="os",
        relname="ipservices",
        objmaps=[
            ObjectMap({"id": "udp_00123"}),
            ObjectMap({"id": "tcp_00022"}),
            ]),

    RelationshipMap(
        modname="Products.ZenModel.IpRouteEntry",
        compname="os",
        relname="routes",
        objmaps=[
            ObjectMap({"id": "0.0.0.0_0"}),
            ObjectMap({"id": "192.168.1.0_24"}),
            ]),

    RelationshipMap(
        modname="Products.ZenModel.IpInterface",
        compname="os",
        relname="interfaces",
        objmaps=[
            ObjectMap({"id": "lo"}),
            ObjectMap({"id": "eth0"}),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.FileSystem",
        compname="os",
        relname="filesystems",
        objmaps=[
            ObjectMap({
                "id": "boot",
                "mount": "/boot",
                }),
            ObjectMap({
                "id": "-",
                "mount": "/",
                }),
            ObjectMap({
                "id": "data",
                "mount": "/data",
                }),
            ObjectMap({
                "id": "snapshots_data_yesterday",
                "mount": "/snapshots/data/yesterday",
                }),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.HardDisk",
        compname="hw",
        relname="harddisks",
        objmaps=[
            ObjectMap({"id": "disk-sda"}),
            ObjectMap({
                "id": "disk-sda1",
                "major_minor": "8:1",
                "mount": "/boot",
                }),
            ObjectMap({
                "id": "disk-sda2",
                "major_minor": "8:2",
                }),
            ObjectMap({
                "id": "disk-sdb",
                "major_minor": "9:0",
                }),
            ObjectMap({
                "id": "disk-sdc",
                "major_minor": "10:0",
                }),
            ObjectMap({
                "id": "disk-os-root",
                "major_minor": "252:0",
                }),
            ObjectMap({
                "id": "disk-data-data",
                "major_minor": "252:1",
                }),
            ObjectMap({
                "id": "disk-data-_snapshot-f005ba11",
                "major_minor": "252:2",
                }),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.VolumeGroup",
        relname="volumeGroups",
        objmaps=[
            ObjectMap({"id": "vg-os"}),
            ObjectMap({"id": "vg-data"}),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.PhysicalVolume",
        relname="physicalVolumes",
        objmaps=[
            ObjectMap({
                "id": "pv-dev_sda2",
                "harddisk_id": "disk-sda2",
                "set_volumeGroup": "vg-os",
                }),
            ObjectMap({
                "id": "pv-dev_sdb",
                "harddisk_id": "disk-sdb",
                "set_volumeGroup": "vg-data",
                }),
            ObjectMap({
                "id": "pv-dev_sdc",
                "harddisk_id": "disk-sdc",
                "set_volumeGroup": "vg-data",
                }),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.LogicalVolume",
        compname="volumeGroups/vg-os",
        relname="logicalVolumes",
        objmaps=[
            ObjectMap({
                "id": "lv-os_root",
                "major_minor": "252:0",
                "mountpoint": "/",
                }),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.LogicalVolume",
        compname="volumeGroups/vg-data",
        relname="logicalVolumes",
        objmaps=[
            ObjectMap({
                "id": "lv-data_data",
                "major_minor": "252:1",
                "mountpoint": "/data",
                }),
            ]),

    RelationshipMap(
        modname="ZenPacks.zenoss.LinuxMonitor.SnapshotVolume",
        compname="volumeGroups/vg-data/logicalVolumes/lv-data_data",
        relname="snapshotVolumes",
        objmaps=[
            ObjectMap({
                "id": "lv-data_snapshot-deadbeef",
                "major_minor": "252:2",
                "mountpoint": "/snapshots/data/yesterday",
                }),
            ]),
]


class migrateTests(zenpacklib.TestCase):
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

    @unittest.skip("non-deterministic test that can fail on slow systems")
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


def create_device(dmd, zPythonClass, device_id, datamaps):
    device = dmd.Devices.findDeviceByIdExact(device_id)
    if not device:
        deviceclass = dmd.Devices.createOrganizer("/Server/SSH/Linux")
        deviceclass.setZenProperty("zPythonClass", zPythonClass)
        device = deviceclass.createInstance(device_id)

    adm = ApplyDataMap()._applyDataMap

    [adm(device, datamap) for datamap in datamaps]

    return device
