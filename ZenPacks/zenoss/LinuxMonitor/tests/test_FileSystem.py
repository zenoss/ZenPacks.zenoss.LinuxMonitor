##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.RRDTemplate import manage_addRRDTemplate

from ZenPacks.zenoss.ZenPackLib import zenpacklib
from ..FileSystem import FileSystem

zenpacklib.enableTesting()


class FileSystemTests(zenpacklib.TestCase):
    def afterSetUp(self):
        super(FileSystemTests, self).afterSetUp()

        dc = self.dmd.Devices.createOrganizer("/Server/SSH/Linux")
        dc.setZenProperty("zPythonClass", "ZenPacks.zenoss.LinuxMonitor.LinuxDevice")

        self.device = dc.createInstance("linux-FileSystemTests")
        self.device.setManageIp("127.0.0.1")
        self.device.setPerformanceMonitor("localhost")

    def test_getRRDTemplates(self):
        boot_fs = FileSystem("boot")
        boot_fs.mount = "/boot"
        boot_fs.type = "ext4"
        self.device.os.filesystems._setObject(boot_fs.id, boot_fs)
        boot_fs = self.device.os.filesystems.boot

        nfs_fs = FileSystem("nfs")
        nfs_fs.mount = "/nfs"
        nfs_fs.type = "nfs"
        self.device.os.filesystems._setObject(nfs_fs.id, nfs_fs)
        nfs_fs = self.device.os.filesystems.nfs

        nfs4_fs = FileSystem("nfs4")
        nfs4_fs.mount = "/nfs4"
        nfs4_fs.type = "nfs4"
        self.device.os.filesystems._setObject(nfs4_fs.id, nfs4_fs)
        nfs4_fs = self.device.os.filesystems.nfs4

        # No templates exist.
        boot_templates = boot_fs.getRRDTemplates()
        self.assertEqual(len(boot_templates), 0)

        nfs_templates = nfs_fs.getRRDTemplates()
        self.assertEqual(len(nfs_templates), 0)

        # Only the FileSystem template exists.
        manage_addRRDTemplate(self.dmd.Devices.rrdTemplates, "FileSystem")

        boot_templates = boot_fs.getRRDTemplates()
        self.assertEqual(len(boot_templates), 1)
        self.assertEqual(boot_templates[0].id, "FileSystem")

        nfs_templates = nfs_fs.getRRDTemplates()
        self.assertEqual(len(nfs_templates), 0)

        # FileSystem and FileSystem_NFS_Client templates exist.
        manage_addRRDTemplate(self.dmd.Devices.rrdTemplates, "FileSystem_NFS_Client")

        boot_templates = boot_fs.getRRDTemplates()
        self.assertEqual(len(boot_templates), 1)
        self.assertEqual(boot_templates[0].id, "FileSystem")

        nfs_templates = nfs_fs.getRRDTemplates()
        self.assertEqual(len(nfs_templates), 1)
        self.assertEqual(nfs_templates[0].id, "FileSystem_NFS_Client")

        nfs4_templates = nfs4_fs.getRRDTemplates()
        self.assertEqual(len(nfs4_templates), 1)
        self.assertEqual(nfs4_templates[0].id, "FileSystem_NFS_Client")
