##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


"""
A command parser

    Command
        /usr/bin/iostat -x

    Datapoints:
        % util

    Example command output
Linux 3.2.0-29-generic (qa-ubuntu-12)   12/31/2018      _x86_64_        (2 CPU)

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.00     0.19    0.84    0.31     0.00     0.00    10.89     0.00    1.23    0.99    1.90   0.60   0.07
sda1              0.00     0.00    0.07    0.00     0.00     0.00     4.05     0.00    3.69    3.69    4.31   3.04   0.02
sda2              0.00     0.00    0.00    0.00     0.00     0.00     2.00     0.00   14.00   14.00    0.00  14.00   0.00
sda5              0.00     0.19    0.77    0.31     0.00     0.00    11.32     0.00    1.08    0.75    1.90   0.53   0.06
sdb               0.00     0.00    0.86    0.00     0.00     0.00    10.00     0.00    0.79    0.79   44.00   0.44   0.04
sdb1              0.00     0.00    0.86    0.00     0.00     0.00    10.00     0.00    0.79    0.79   44.00   0.44   0.04
sdc               0.00     0.00    0.86    0.00     0.00     0.00    10.00     0.00    1.22    1.22   80.00   0.57   0.05
sdc1              0.00     0.00    0.86    0.00     0.00     0.00    10.00     0.00    1.22    1.22   80.00   0.57   0.05
dm-0              0.00     0.00    0.07    0.00     0.00     0.00     8.00     0.00    0.89    0.89   44.00   0.72   0.00
dm-1              0.00     0.00    0.07    0.00     0.00     0.00     8.00     0.00    1.71    1.71   80.00   1.14   0.01
dm-2              0.00     0.00    0.07    0.51     0.00     0.00    11.46     0.00    1.28    0.87    1.34   0.48   0.03
dm-3              0.00     0.00    0.07    0.00     0.00     0.00     8.00     0.00    2.02    2.02    0.00   1.39   0.01

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda2              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sda5              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sdb               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sdb1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sdc               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
sdc1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
dm-0              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
dm-1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
dm-2              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
dm-3              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00

"""

import logging
import re
from pprint import pformat

from Products.ZenRRD.CommandParser import  CommandParser


LOG = logging.getLogger('zen.command.parsers.iostat')
COMPONENT_PARSER = r'^(?P<component>\S+)[\s\t]'
SCANNER = r"(?P<component>\S+)[\s\t].*\s+(?P<{}>\d+[.,]\d+$|\d+$)"
COMPONENT_SPLITTER = "\n"
COMPONENT_ID_PATTERN = r"disk-{0}"


class iostats(CommandParser):


    def processResults(self, cmd, result):
        """
        :param cmd:
        :param result:
        :return:
        """
        if cmd.result.output:
            output = cmd.result.output.split("%util")
            if len(output) == 3:
                scanner = SCANNER.format("bandwidthUtilCurrent")
                self.getMetrics(cmd, output[2], result, scanner)
                scanner = SCANNER.format("bandwidthUtilAvg")
                self.getMetrics(cmd, output[1], result, scanner)
        return result

    def getMetrics(self, cmd, output, result, scanner):
        """

        :param cmd:
        :param output:
        :param result:
        :return:
        """
        parts = output.split(COMPONENT_SPLITTER)
        for part in parts:
            match = re.search(scanner, part)
            if not match:
                continue
            matchDict = match.groupdict()
            component = matchDict["component"]
            componentPattern = COMPONENT_ID_PATTERN.format(component)
            matchobj = re.search(componentPattern, cmd.component)
            if matchobj:
                for dp in cmd.points:
                    dpValue = matchDict.get(dp.id)
                    if dpValue is not None:
                        result.values.append((dp, float(dpValue)))
