##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Update zLinuxServicesModeled and zLinuxServicesNotModeled properties."""

# Zenoss Imports
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration


class UpdateModeledServices(ZenPackMigration):
    version = Version(2, 3, 2)

    def migrate(self, pack):
        try:
            device_class = pack.dmd.Devices.Server.SSH.Linux
        except Exception:
            return

        modeled_property = "zLinuxServicesModeled"
        modeled_value = device_class.getZ(modeled_property, [])

        # Change from initial default of [".*"] to [].
        if modeled_value == [".*"]:
            device_class.setZenProperty(modeled_property, [])

        not_modeled_property = "zLinuxServicesNotModeled"
        not_modeled_value = device_class.getZ(not_modeled_property, [])

        # Change from initial default of [] to list of problematic services.
        if not_modeled_value == []:
            device_class.setZenProperty(
                not_modeled_property, sorted([
                    # No good status: Ubuntu <= 14
                    "ondemand",
                    "pppd-dns",
                    "rsync",
                    "sudo",

                    # No good status: RHEL 5
                    "anacron",
                    "cpuspeed",
                    "firstboot",
                    "irqbalance",
                    "isdn",
                    "lvm2-monitor",
                    "mdmonitor",
                    "rpcgssd",

                    # No good status: CentOS 5
                    "mcstrans",

                    # No good status: CentOS 6
                    "bluetooth",
                    "portreserve",
                    "sysstat",
                    ]))
