##############################################################################
#
# Copyright (C) Zenoss, Inc. 2008, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


import re

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.LinuxMonitor.util import LVMAttributeParser
from Products.ZenUtils.Utils import prepId

'''
We'll only look at state and health for now, but if we need any of the following in the future, 
we only need to add the datapoint and handler
# State: (a)ctive, (s)uspended, (I)nvalid snapshot, invalid (S)uspended snapshot,
        snapshot (m)erge failed, suspended snapshot (M)erge failed,
        mapped (d)evice present without tables, mapped device present with (i)nactive table
# Volume Health: (p)artial, (r)efresh needed, (m)ismatches exist, (w)ritemostly, (X) unknown

sample output:
VG_LV Attr
centos_root -wi-ao----
centos_swap -wi-ao----
fileserver_backup -wi-ao----
fileserver_inactive -wi-------
fileserver_media -wi-ao----
fileserver_share owi-aos---
fileserver_snap swi-a-s---

'''


class lvsstatus(CommandParser):

    scanner = r'(?P<component>\S+) *(?P<attributes>\S+)'

    componentScanValue = 'id'

    lvm_parser = LVMAttributeParser()

    def dataForParser(self, context, dp):
        # Borrowed from ComponentCommandParser
        # This runs in the zenhub service, so it has access to the actual ZODB object
        return dict(componentScanValue=getattr(context, self.componentScanValue))

    def processResults(self, cmd, result):
        lv_atts = {'type': 0, 'permissions': 1, 'allocation': 2, 'fixed': 3, 'state': 4, 'device': 5, 'type': 6, 'zeroes': 7, 'health': 8, 'skip': 9}
        self._cmd = cmd
        for dp in cmd.points:
            if dp.id not in lv_atts:
                continue
            dp.component = dp.data['componentScanValue']
            for line in cmd.result.output.split('\n'):
                match = re.search(self.scanner, line)
                if not match or dp.component != match.groupdict()['component']:
                    continue
                value = 'None'
                if dp.id == 'state':
                    event, value = self.handleState(dp.component, match.groupdict()['attributes'][lv_atts[dp.id]])
                elif dp.id == 'health':
                    event = self.handleHealth(dp.component, match.groupdict()['attributes'][lv_atts[dp.id]])
                event['device'] = cmd.deviceConfig.name
                event['component'] = prepId(dp.component)
                event['eventClass'] = cmd.eventClass
                result.events.append(event)
                if value != 'None':
                    result.values.append((dp, float(value)))

        return result

    def handleState(self, component, attribute):
        if attribute == 'a':
            summary = '{} in active state'.format(component)
            severity = 0
            value = 1
        else:
            reason = self.lvm_parser.lv_state(attribute)
            if not reason:
                reason = 'Inactive'
            summary = '{} not active: {}'.format(component, reason)
            severity = self._cmd.severity
            value = 0
        return ({
            'summary': summary,
            'severity': severity,
        },
            value)

    def handleHealth(self, component, attribute):
        if attribute == '-':
            summary = '{} healthy'.format(component)
            severity = 0
        else:
            reason = self.lvm_parser.lv_health(attribute)
            summary = '{} not healthy: {}'.format(component, reason)
            severity = self._cmd.severity
        return {
            'summary': summary,
            'severity': severity,
        }
