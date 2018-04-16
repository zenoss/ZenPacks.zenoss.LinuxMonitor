##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


from Products.ZenRRD.CommandParser import CommandParser

MULTIPLIER = {
    'kB' : 1024,
    'MB' : 1024 * 1024,
    'b' : 1
}

class mem(CommandParser):

    def processResults(self, cmd, result):
        """
        Process the results of "cat /proc/meminfo".
        """
        datapointMap = dict([(dp.id, dp) for dp in cmd.points])
        data = [line.split(':', 1) for line in cmd.result.output.splitlines()]

        # For derivatives we always need to consider some keys.
        desiredKeys = frozenset(
            datapointMap.keys() + ["MemFree", "MemTotal", "MemAvailable"])

        # Extract values from data. Convert values to bytes.
        values = {}
        for id, vals in data:
            if id in desiredKeys:
                try:
                    value, unit = vals.strip().split()
                except Exception:
                    value, unit = vals, "b"

                values[id] = int(value) * MULTIPLIER.get(unit, 1)

        # MemAvailable is useful, but only introduced in Linux 3.14.
        # https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773
        if "MemAvailable" not in values:
            if "MemFree" not in values:
                return result
            # Naively use MemFree for MemAvailable on older kernels. It's
            # "pretty much guaranteed to be wrong today", but we don't have the
            # /proc/zoneinfo information to calculate MemAvailable here.
            values["MemAvailable"] = values["MemFree"]

        # Derivatives.
        values["MemUsed"] = values["MemTotal"] - values["MemAvailable"]
        values["MemUsedPercent"] = (
            float(values["MemUsed"]) / float(values["MemTotal"])) * 100.0
        if datapointMap.get("MemAdjustedUsed"):
            values["MemAdjustedUsed"] = values["MemTotal"] - (values["MemFree"] + values["Buffers"] + values["Cached"])
        if datapointMap.get("MemAdjustedUsedPercent"):
            values["MemAdjustedUsedPercent"] = ((float(values["MemTotal"] - (values["MemFree"] + values["Buffers"] + values["Cached"])) )/ float(values["MemTotal"])) * 100.0

        # Add all requested values to result.
        result.values.extend(
            (datapointMap[k], v) for k, v in values.items()
            if k in datapointMap)

        return result
