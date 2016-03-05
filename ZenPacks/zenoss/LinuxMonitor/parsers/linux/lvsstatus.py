##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Parse results of lvm2 "lvs" command.

We'll only look at state and health for now, but if we need any of the
following in the future, we only need to add the datapoint and handler.

# State: (a)ctive, (s)uspended, (I)nvalid snapshot, invalid (S)uspended snapshot,
        snapshot (m)erge failed, suspended snapshot (M)erge failed,
        mapped (d)evice present without tables, mapped device present with (i)nactive table
# Volume Health: (p)artial, (r)efresh needed, (m)ismatches exist, (w)ritemostly, (X) unknown

CentOS 7 sample output:

  centos         home                                           -wi-ao----
  cinder-volumes _snapshot-9985dbc7-ff68-4cfd-b84d-6ce372afa3aa swi-a-s---
  cinder-volumes volume-055e2dce-b50b-468b-af40-21b634a06280    -wi-a-----

Ubuntu 14.04 sample output:

  data docker     twi-i-tz-
  data regularLV1 -wi-ao---
  data serviced   twi-i-tz-

"""

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.LinuxMonitor.util import LVMAttributeParser
from Products.ZenUtils.Utils import prepId


class lvsstatus(CommandParser):

    lvm_parser = LVMAttributeParser()

    def dataForParser(self, context, dp):
        """Add additional data to dp for the processResults method.

        This method is executed in zenhub, so context will be a full
        LogicalVolume or SnapshotVolume object.

        """
        return {
            'vgname': getattr(context, 'vgname', None),
            'lvname': getattr(context, 'title', None),
            }

    def processResults(self, cmd, result):
        lv_atts = {
            'type': 0,
            'permissions': 1,
            'allocation': 2,
            'fixed': 3,
            'state': 4,
            'device': 5,
            'type': 6,
            'zeroes': 7,
            'health': 8,
            'skip': 9,
            }

        for dp in cmd.points:
            if dp.id not in lv_atts:
                continue

            for line in cmd.result.output.split('\n'):
                try:
                    vg_name, lv_name, lv_attr = line.strip().split()
                except ValueError:
                    continue

                # Verify that this line is for the appropriate component.
                if vg_name != dp.data['vgname'] or lv_name != dp.data['lvname']:
                    continue

                # Extract specific attribute value from lv_attr string.
                av = lv_attr[lv_atts[dp.id]]

                if dp.id == 'state':
                    event, value = self.handleState(cmd, dp.component, av)
                elif dp.id == 'health':
                    event, value = self.handleHealth(cmd, dp.component, av)
                else:
                    # No handler for this attribute.
                    continue

                # Add default event fields to events returned by handler.
                result.events.append(dict({
                    'device': cmd.deviceConfig.name,
                    'component': prepId(dp.component),
                    'eventClass': cmd.eventClass,
                    }, **event))

                if value is not None:
                    result.values.append((dp, float(value)))

        return result

    def handleState(self, cmd, component, attribute):
        if attribute == 'a':
            return ({
                'summary': '{} in active state'.format(component),
                'severity': 0,
                }, 1)
        else:
            reason = self.lvm_parser.lv_state(attribute) or 'Inactive'
            return ({
                'summary': '{} not active: {}'.format(component, reason),
                'severity': cmd.severity,
                }, 0)

    def handleHealth(self, cmd, component, attribute):
        if attribute == '-':
            return ({
                'summary': '{} healthy'.format(component),
                'severity': 0,
                }, None)
        else:
            reason = self.lvm_parser.lv_health(attribute)
            return ({
                'summary': '{} not healthy: {}'.format(component, reason),
                'severity': cmd.severity,
                }, None)
