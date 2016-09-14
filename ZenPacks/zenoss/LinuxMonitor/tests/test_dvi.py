##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import unittest

from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.LinuxMonitor import zenpacklib
from ZenPacks.zenoss.LinuxMonitor.tests import utils as tu

try:
    from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS
    DYNAMICVIEW_INSTALLED = True
except ImportError:
    TAG_IMPACTED_BY, TAG_IMPACTS = None, None
    DYNAMICVIEW_INSTALLED = False

try:
    import ZenPacks.zenoss.Impact  # NOQA
    IMPACT_INSTALLED = True
except ImportError:
    IMPACT_INSTALLED = False


# These are the DynamicView/Impact impactful relationships we'll test for.
EXPECTED_IMPACTS = """
// Device
[test-linux1]->[docker]
[test-linux1]->[memcached]
[test-linux1]->[tcp_00022]
[test-linux1]->[udp_00123]
[test-linux1]->[lo]
[test-linux1]->[eth0]
[test-linux1]->[0]
[test-linux1]->[1]
[test-linux1]->[disk-sda]
[test-linux1]->[disk-sda1]
[test-linux1]->[disk-sda2]
[test-linux1]->[disk-sdb]
[test-linux1]->[disk-sdc]
[test-linux1]->[disk-os-root]
[test-linux1]->[disk-data-data]
[test-linux1]->[disk-data-_snapshot-f005ba11]
// HardDisk
[disk-sda1]->[boot]
[disk-sda2]->[pv-dev_sda2]
[disk-sdb]->[pv-dev_sdb]
[disk-sdc]->[pv-dev_sdc]
[disk-os-root]->[lv-os_root]
[disk-data-data]->[lv-data_data]
[disk-data-_snapshot-f005ba11]->[lv-data_snapshot-deadbeef]
// PhysicalVolume
[pv-dev_sda2]->[vg-os]
[pv-dev_sdb]->[vg-data]
[pv-dev_sdc]->[vg-data]
// VolumeGroup
[vg-os]->[lv-os_root]
[vg-data]->[lv-data_data]
// LogicalVolume
[lv-os_root]->[-]
[lv-data_data]->[data]
[lv-data_data]->[lv-data_snapshot-deadbeef]
// SnapshotVolume
[lv-data_snapshot-deadbeef]->[snapshots_data_yesterday]
"""

DYNAMIC_VIEW_EXPECTING_MISSING = """
//Dynamic View Interface
[eth0]->[test-linux1]
[lo]->[test-linux1]
"""

# It's OK if these are missing from DynamicView, but not from Impact.
EXPECTED_MISSING_FROM_DV = """
[test-linux1]->[docker]
[test-linux1]->[memcached]
[test-linux1]->[tcp_00022]
[test-linux1]->[udp_00123]
[test-linux1]->[0]
[test-linux1]->[1]
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


# Testing must be enabled before zenpacklib.TestCase can be used.
zenpacklib.enableTesting()


class TestDVI(zenpacklib.TestCase):

    def afterSetUp(self):
        super(TestDVI, self).afterSetUp()

        # OpenStack integration assumes /OpenStack/Infrastructure device class.
        self.dmd.Devices.createOrganizer("/OpenStack/Infrastructure")

        # Create a fully-modeled device.
        self.device = tu.create_device(
            self.dmd,
            "ZenPacks.zenoss.LinuxMonitor.LinuxDevice",
            "test-linux1",
            DATAMAPS)

    @unittest.skipUnless(DYNAMICVIEW_INSTALLED, "DynamicView not installed")
    def test_DynamicView_Impacts(self):
        expected = tu.triples_from_yuml(EXPECTED_IMPACTS)
        all_expected = tu.complement_triples(expected)

        expected_missing = tu.triples_from_yuml(EXPECTED_MISSING_FROM_DV)
        all_expected_missing = tu.complement_triples(expected_missing)
        dynamic_view = tu.triples_from_yuml(DYNAMIC_VIEW_EXPECTING_MISSING)
        missing_dynamic_view = tu.complement_triples(dynamic_view)

        found = tu.dynamicview_triples_from_device(
            self.device, tags=(TAG_IMPACTS, TAG_IMPACTED_BY))

        missing = all_expected - (found | all_expected_missing)
        extra = (found | all_expected_missing) - (all_expected | missing_dynamic_view)

        self.assertFalse(
            missing or extra,
            "DynamicView {}/{} relationship issue(s):\n\n{}".format(
                TAG_IMPACTED_BY, TAG_IMPACTS,
                tu.yuml_from_triples(
                    expected,
                    missing=missing,
                    extra=extra,
                    tag_map={
                        TAG_IMPACTS: TAG_IMPACTED_BY,
                        })))

    @unittest.skipUnless(IMPACT_INSTALLED, "Impact not installed")
    def test_Impact_Edges(self):
        expected = tu.triples_from_yuml(EXPECTED_IMPACTS)
        all_expected = tu.complement_triples(expected)
        found = tu.impact_triples_from_device(self.device)

        missing = all_expected - found
        extra = found - all_expected

        self.assertFalse(
            missing or extra,
            "Impact edges issue(s):\n\n{}".format(
                tu.yuml_from_triples(
                    expected,
                    missing=missing,
                    extra=extra,
                    tag_map={
                        TAG_IMPACTS: TAG_IMPACTED_BY,
                        })))
