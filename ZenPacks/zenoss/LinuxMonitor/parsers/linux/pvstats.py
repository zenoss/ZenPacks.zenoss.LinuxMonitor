##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import re
import logging
from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

log = logging.getLogger("zen.command.parsers.pvstats")

class pvstats(ComponentCommandParser):

    componentSplit = '\n'

    componentScanner = '(?P<component>\S+)'

    scanners = [
        r'\S+ *(?P<size>\d+) *(?P<free>\d+)'
    ]

    def processResults(self, cmd, result):
        ifs = {}
        for dp in cmd.points:
            dp.component = dp.data['componentScanValue']
            points = ifs.setdefault(dp.component.split('-')[-1], {})
            points[dp.id] = dp

        parts = cmd.result.output.split(self.componentSplit)

        for part in parts:
            match = re.search(self.componentScanner, part)
            if not match:
                continue

            component = match.groupdict()['component'].strip()
            if self.componentScanValue == 'id':
                component = self.prepId(component)

            points = ifs.get(component, None)
            if not points:
                continue

            for search in self.scanners:
                match = re.search(search, part)
                if match:
                    for name, value in match.groupdict().items():
                        dp = points.get(name, None)
                        if dp is not None:
                            if value in ('-', ''):
                                value = 0
                            result.values.append((dp, float(value)))
        log.debug(result)
        return result
