##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Update the /Perf/Filesystem transform to work with percentUsed datapoint."""

import hashlib
import logging

from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

LOG = logging.getLogger("zen.migrate")

NEW_TRANSFORM = """
def transform():
    if component and evt.eventKey:
        try:
            current = float(evt.current)
            totalBytes = int(component.totalBytes())
        except Exception:
            return

        if totalBytes < 1:
            return

        usedPercent, usedBytes, freeBytes = None, None, None

        # SNMP (Platform)
        if 'usedBlocks' in evt.eventKey:
            usedBytes = int(current) * component.blockSize
            usedPercent = (usedBytes / totalBytes) * 100.0
            freeBytes = totalBytes - usedBytes

        # Linux SSH (LinuxMonitor ZenPack)
        elif 'percentUsed' in evt.eventKey:
            usedPercent = current
            usedBytes = totalBytes * (current * 0.01)
            freeBytes = totalBytes - usedBytes

        # Windows (Windows ZenPacks)
        elif 'FreeMegabytes' in evt.eventKey:
            freeBytes = int(current) * 1048576
            usedBytes = totalBytes - freeBytes
            usedPercent = (usedBytes / totalBytes) * 100.0

        else:
            return

        # Make a nicer event summary.
        from Products.ZenUtils.Utils import convToUnits
        evt.summary = "disk space threshold: %3.1f%% used (%s free)" % (
            usedPercent, convToUnits(freeBytes))
        evt.message = evt.summary

transform()
""".strip()

# MD5 hex digest of default transform in Zenoss 5.2.4.
ORIGINAL_DIGEST = "18c01c20b29fef6f0b097a8bea443fa6"


class UpdateFileSystemTransform(ZenPackMigration):
    version = Version(2, 2, 3)

    def migrate(self, pack):
        eventclass = pack.dmd.Events.createOrganizer("Perf/Filesystem")
        transform = eventclass.transform or ""

        # No need to do anything if the transform is already updated.
        if transform == NEW_TRANSFORM:
            return

        # Avoid overwriting custom transform, but offer the user enough
        # information to update it on their own if they so choose.
        if hashlib.md5(transform).hexdigest() != ORIGINAL_DIGEST:
            LOG.warning(
                "Not updating /Perf/Filesystem transform because it has been customized\n"
                "\n"
                "It would have been updated to the following otherwise.\n"
                "\n"
                "%s",
                NEW_TRANSFORM)

            return

        LOG.info("Updating /Perf/Filesystem transform for percentUsed datapoint")
        eventclass.transform = NEW_TRANSFORM
