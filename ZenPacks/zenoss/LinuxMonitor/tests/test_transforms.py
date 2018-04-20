##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Event transform tests."""

from ZenPacks.zenoss.ZenPackLib import zenpacklib
from .. import transforms

zenpacklib.enableTesting()


class TransformsTests(zenpacklib.TestCase):

    """Test suite for event transforms."""

    maxDiff = None

    def test_install_transforms(self):
        eventclass = self.dmd.Events.createOrganizer("/Perf/Filesystem")

        # Test that a custom transform is not replaced.
        eventclass.transform = CUSTOM_TRANSFORM
        transforms.install_transforms(self.dmd)
        self.assertMultiLineEqual(
            eventclass.transform,
            CUSTOM_TRANSFORM)

        # Test that the correct transform is not replaced.
        eventclass.transform = transforms.PERF_FILESYSTEM_TRANSFORM
        transforms.install_transforms(self.dmd)
        self.assertMultiLineEqual(
            eventclass.transform,
            transforms.PERF_FILESYSTEM_TRANSFORM)

        # Test that an empty transform is not replaced. (empty is custom)
        eventclass.transform = ""
        transforms.install_transforms(self.dmd)
        self.assertMultiLineEqual(
            eventclass.transform,
            "")

        # Test that the default platform transform is replaced.
        eventclass.transform = ORIGINAL_TRANSFORM
        transforms.install_transforms(self.dmd)
        self.assertMultiLineEqual(
            eventclass.transform,
            transforms.PERF_FILESYSTEM_TRANSFORM)

        # Test that a broken old LinuxMonitor transform is replaced.
        eventclass.transform = BROKEN_LINUX_TRANSFORM
        transforms.install_transforms(self.dmd)
        self.assertMultiLineEqual(
            eventclass.transform,
            transforms.PERF_FILESYSTEM_TRANSFORM)


CUSTOM_TRANSFORM = """
evt.summary = "transformed!"
""".strip()

ORIGINAL_TRANSFORM = """
if device and evt.eventKey:
    for f in device.os.filesystems():
        if f.name() != evt.component and f.id != evt.component: continue

        # Extract the used blocks from the event's message
        import re
        m = re.search("threshold of [^:]+: current value ([\d\.]+)", evt.message)
        if not m: continue

        # Get the total blocks from the model. Adjust by specified offset.
        totalBlocks = f.totalBlocks * getattr(device, "zFileSystemSizeOffset", 1.0)
        totalBytes = totalBlocks * f.blockSize
        usedBytes = None

        currentValue = float(m.groups()[0])
        if 'usedBlocks' in evt.eventKey:
            usedBytes = currentValue * f.blockSize
        elif 'FreeMegabytes' in evt.eventKey:
            usedBytes = totalBytes - (currentValue * 1048576)
        else:
            continue

        try:
            # Calculate the used percent and amount free.
            usedBlocks = float(m.groups()[0])
            p = (usedBytes / totalBytes) * 100
            from Products.ZenUtils.Utils import convToUnits
            free = convToUnits(totalBytes - usedBytes)
            # Make a nicer summary
            evt.summary = "disk space threshold: %3.1f%% used (%s free)" % (p, free)
            evt.message = evt.summary
        except ZeroDivisionError, e:
            # Total size hasn't been calculated
            pass

        break
""".strip()

BROKEN_LINUX_TRANSFORM = """
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
