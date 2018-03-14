##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration


class AddRelations(ZenPackMigration):
    version = Version(2, 3, 0)

    def migrate(self, pack):
        dc = pack.dmd.Devices.Server.SSH.Linux
        for d in dc.getSubDevicesGen():

            for volumeGroup in d.volumeGroups():
                if not hasattr(volumeGroup, 'thinPools'):
                    volumeGroup.buildRelations()
                for logicalVolume in volumeGroup.logicalVolumes():
                    if not hasattr(logicalVolume, 'thinPool'):
                        logicalVolume.buildRelations()

AddRelations()
