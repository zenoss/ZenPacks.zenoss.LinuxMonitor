#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.os_service \
    import SERVICE_MAP

log = logging.getLogger("zen.command.parsers.service")

ON_STATUS = ['active', 'running']


class service(CommandParser):

    def processResults(self, cmd, result):

        if cmd.result.exitCode != 0:
            return

        log.debug(cmd.result.output)

        services = cmd.result.output.splitlines()
        initService = SERVICE_MAP.get(services[0])

        if not initService:
            log.debug("Cannot parse OS services, init service is unknown!")
            return result

        services = services[1:]
        regex = initService.get('regex')
        functions = initService.get('functions')
        if functions:
            services = functions.get('services')(services)

        status_value = 1    # Status On/Active
        severity = 0        # Clear
        event_status = 'up'
        for line in services:
            line = line.strip()
            match = regex.match(line)

            if not match:
                continue

            groupdict = match.groupdict()
            title = groupdict.get('title')

            if cmd.component != title:
                continue

            active_status = groupdict.get('active_status')
            status_string = active_status.split()[0]

            if status_string not in ON_STATUS:
                status_value = 0    # STATUS OFF/INACTIVE
                severity = cmd.severity
                event_status = 'down'

            result.events.append({
                'device': cmd.deviceConfig.device,
                'component': cmd.component,
                'severity': severity,
                'eventClass': cmd.eventClass,
                'eventClassKey': "{}|{}".format("linux-services",
                                                cmd.component),
                'summary': 'OS Service is {}'.format(event_status),
                'message': '{} is {}'.format(title, active_status)
                })
            break

        for dp in cmd.points:
            if 'status' in dp.id:
                result.values.append((dp, status_value))

        return result
