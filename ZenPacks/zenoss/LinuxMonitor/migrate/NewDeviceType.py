##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Convert Linux devices under /Server/SSH/Linux to LinuxDevice type.

Prior to version 2.0.0 of the LinuxMonitor ZenPack, Linux devices were the
default Products.ZenModel.Device type. A specialized type,
ZenPacks.zenoss.LinuxMonitor.LinuxDevice, was added in version 2.0.0 to add
some LVM relationships and specialized DynamicView adapters.

"""

# If the migration takes longer than this interval, a running progress
# showing elapsed and estimated remaining time will be logged this
# often. The value is in seconds.
PROGRESS_LOG_INTERVAL = 10

PROP_zPythonClass = "zPythonClass"
DEVICECLASS = "/Server/SSH/Linux"
FROM_zPythonClasses = ("", "Products.ZenModel.Device")
TO_zPythonClass = "ZenPacks.zenoss.LinuxMonitor.LinuxDevice"


import logging
LOG = logging.getLogger("zen.LinuxMonitor.migrate.{}".format(__name__))

import contextlib

from Products.ZenModel.Device import Device as BaseDevice
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.Zuul.interfaces import ICatalogTool

from ZenPacks.zenoss.LinuxMonitor import progresslog
from ZenPacks.zenoss.LinuxMonitor.LinuxDevice import LinuxDevice

try:
    from Products.ZenUtils.events import pausedAndOptimizedReindexing
except ImportError:
    # Implement our own do-nothing version if this Zenoss doesn't have it.
    @contextlib.contextmanager
    def pausedAndOptimizedReindexing():
        yield


@contextlib.contextmanager
def logLevel(name, level=logging.NOTSET):
    """Context manager that change the level of named logger."""
    named_log = logging.getLogger(name)
    named_log_level = named_log.level
    named_log.level = level
    yield
    named_log.setLevel(named_log_level)


class NewDeviceType(ZenPackMigration):

    version = Version(2, 0, 0)

    def migrate(self, pack):
        dmd = pack.getDmd()

        try:
            deviceclass = dmd.Devices.getOrganizer(DEVICECLASS)
        except Exception:
            return

        # This would be done by zenpacklib, but good to log it and be explicit.
        if deviceclass.getZ(PROP_zPythonClass) != TO_zPythonClass:
            LOG.info(
                "changing %s %s to %s",
                deviceclass.getOrganizerName(),
                PROP_zPythonClass,
                TO_zPythonClass)

            deviceclass.setZenProperty(PROP_zPythonClass, TO_zPythonClass)

        # Remove any overrides of zPythonClass in child device classes.
        for subdc in deviceclass.getSubOrganizers():
            if subdc.hasProperty(PROP_zPythonClass):
                LOG.info(
                    "removing %s override of %s",
                    subdc.getOrganizerName(),
                    PROP_zPythonClass)

                subdc.deleteZenProperty(PROP_zPythonClass)

        # Estimated total. Only as correct as the global catalog.
        total = ICatalogTool(deviceclass).search(BaseDevice).total
        LOG.info("converting approximately %s devices", total)

        # Add progress indication. This could take a while if there are a lot
        # of Linux devices.
        progress = progresslog.ProgressLogger(
            LOG,
            prefix="progress",
            total=total,
            interval=PROGRESS_LOG_INTERVAL)

        # Move devices that aren't a LinuxDevice back into their same device
        # class. This will cause them to be recreated with the new type. We
        # don't use the catalog to find devices here because we want to be
        # absolutely sure that we convert all devices.
        with pausedAndOptimizedReindexing():
            with logLevel("zen.GraphChangeFactory", level=logging.ERROR):
                for device in deviceclass.getSubDevicesGen_recursive():
                    if not isinstance(device, LinuxDevice):
                        device.changeDeviceClass(
                            device.deviceClass().getOrganizerName())
                        progress.increment()

        LOG.info("finished converting %s devices", progress.pos)
