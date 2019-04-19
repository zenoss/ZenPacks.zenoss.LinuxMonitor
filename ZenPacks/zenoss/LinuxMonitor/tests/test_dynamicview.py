##############################################################################
#
# Copyright (C) Zenoss, Inc. 2019, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

try:
    from ZenPacks.zenoss.DynamicView.tests import DynamicViewTestCase
except ImportError:
    import unittest

    class DynamicViewTestCase(unittest.TestCase):
        """TestCase stub if DynamicViewTestCase isn't available."""

        def check_impacts(self):
            pass


# These are the expected impact relationships.
EXPECTED_IMPACTS = """
// Device
[linux1]->[linux1/docker]
[linux1]->[linux1/memcached]
[linux1]->[linux1/tcp_00022]
[linux1]->[linux1/udp_00123]
[linux1]->[linux1/lo]
[linux1]->[linux1/eth0]
[linux1]->[linux1/disk-sda]
[linux1]->[linux1/disk-sda1]
[linux1]->[linux1/disk-sda2]
[linux1]->[linux1/disk-sdb]
[linux1]->[linux1/disk-sdc]
[linux1]->[linux1/disk-os-root]
[linux1]->[linux1/disk-data-data]
[linux1]->[linux1/disk-data-_snapshot-f005ba11]

// HardDisk
[linux1/disk-sda1]->[linux1/boot]
[linux1/disk-sda2]->[linux1/pv-dev_sda2]
[linux1/disk-sdb]->[linux1/pv-dev_sdb]
[linux1/disk-sdc]->[linux1/pv-dev_sdc]
[linux1/disk-os-root]->[linux1/lv-os_root]
[linux1/disk-data-data]->[linux1/lv-data_data]
[linux1/disk-data-_snapshot-f005ba11]->[linux1/lv-data_snapshot-deadbeef]

// PhysicalVolume
[linux1/pv-dev_sda2]->[linux1/vg-os]
[linux1/pv-dev_sdb]->[linux1/vg-data]
[linux1/pv-dev_sdc]->[linux1/vg-data]

// VolumeGroup
[linux1/vg-os]->[linux1/lv-os_root]
[linux1/vg-data]->[linux1/lv-data_data]

// LogicalVolume
[linux1/lv-os_root]->[linux1/-]
[linux1/lv-data_data]->[linux1/data]
[linux1/lv-data_data]->[linux1/lv-data_snapshot-deadbeef]

// SnapshotVolume
[linux1/lv-data_snapshot-deadbeef]->[linux1/snapshots_data_yesterday]
"""

# This is the Linux device model that we'll be testing.
DATAMAPS = [
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


class DynamicViewTests(DynamicViewTestCase):
    """DynamicView tests."""

    # ZenPacks to initialize for testing purposes.
    zenpacks = [
        "ZenPacks.zenoss.LinuxMonitor",
    ]

    # Expected impact relationships.
    expected_impacts = EXPECTED_IMPACTS

    # Devices to create.
    device_data = {
        "linux1": {
            "deviceClass": "/Server/SSH/Linux",
            "zPythonClass": "ZenPacks.zenoss.LinuxMonitor.LinuxDevice",
            "dataMaps": DATAMAPS,
        }
    }

    def test_impacts(self):
        self.check_impacts()
