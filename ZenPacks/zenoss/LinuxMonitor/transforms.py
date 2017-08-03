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


LOG = logging.getLogger("zen.LinuxMonitor")

# Our desired /Perf/Filesystem transform.
PERF_FILESYSTEM_TRANSFORM = """
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
            usedPercent = (usedBytes / float(totalBytes)) * 100.0
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
            usedPercent = (usedBytes / float(totalBytes)) * 100.0

        else:
            return

        # Make a nicer event summary.
        from Products.ZenUtils.Utils import convToUnits
        evt.summary = "disk space threshold: %3.1f%% used (%s free)" % (
            usedPercent, convToUnits(freeBytes))
        evt.message = evt.summary

transform()
""".strip()

# MD5 hex digests of /Perf/Filesystem transforms that we'll replace.
PERF_FILESYSTEM_ORIGINAL_DIGESTS = (
    "1f4684a04169e0c65bd550fdf0bddbaf",  # Zenoss 2.5.0
    "86930c7a16f80fc1e1fd8971b9c9f3be",  # Zenoss 3
    "b28ad4d2d86b1f23229863a84bf54dec",  # Zenoss 5.1.1
    "18c01c20b29fef6f0b097a8bea443fa6",  # Zenoss 5.2.4
    "2b10c421920843e25c0aba6fb09f37d6",  # LinuxMonitor 2.2.3
)

# Description of transforms we want to install.
EVENT_CLASS_TRANSFORMS = {
    "/Perf/Filesystem": {
        "desired": PERF_FILESYSTEM_TRANSFORM,
        "original_digests": PERF_FILESYSTEM_ORIGINAL_DIGESTS,
    },
}


def install_transforms(dmd):
    """Install all transforms in EVENT_CLASS_TRANSFORMS.

    They will only be installed if the existing transform has not been
    customized by the user.

    """
    for eventclass_name, data in EVENT_CLASS_TRANSFORMS.iteritems():
        try:
            eventclass = dmd.Events.getOrganizer(eventclass_name)
        except KeyError:
            continue
        else:
            install_transform(
                eventclass,
                data.get("desired", ""),
                data.get("original_digests", []))


def install_transform(eventclass, transform, original_digests):
    """Install transform for eventclass.

    It will only be installed if the existing transform has not been
    customized by the user. The original_digests are used to determine if
    the existing transform has been customized. If the MD5 hex digest of the
    existing transform matches on of original_digests, the new transform
    will be installed.

    """
    existing_transform = eventclass.transform or ""
    existing_transform = existing_transform.strip()

    # No need to do anything if the transform is already updated.
    if transform == existing_transform:
        return

    # Avoid overwriting custom transform, but offer the user enough
    # information to update it on their own if they so choose.
    if hashlib.md5(existing_transform).hexdigest() not in original_digests:
        LOG.warning(
            "Not updating /Perf/Filesystem transform because it has been customized\n"
            "\n"
            "It would have been updated to the following otherwise.\n"
            "\n"
            "%s",
            transform)

        return

    LOG.info("Updating /Perf/Filesystem transform for percentUsed datapoint")
    eventclass.transform = transform
