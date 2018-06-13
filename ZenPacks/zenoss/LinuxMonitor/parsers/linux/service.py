#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
from Products.ZenEvents import ZenEventClasses
from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.os_service \
    import SERVICE_MAP

log = logging.getLogger("zen.command.parsers.service")

ON_STATUS = ['active',                  # Systemd status up
             'running']                 # SystemV and Upstart status up

SYSV_EXIT_CODE = {
    '0': 'program is running or service is OK',
    '1': 'program is dead and /var/run pid file exists',
    '2': 'program is dead and /var/lock lock file exists',
    '3': 'program is not running',
    '4': 'program or service status is unknown'
}


class service(CommandParser):
    def dataForParser(self, context, datapoint):
        return dict(id=context.name())

    def processResults(self, cmd, result):
        if cmd.result.exitCode != 0:
            return

        log.debug(cmd.result.output)

        # Init default values for 'active' clear event
        status_value = 1    # Status On/Active
        severity = 0        # Clear
        event_status = 'up'
        name = cmd.component

        # Parse service string from output and find if systemd or systemV
        services = cmd.result.output.splitlines()

        # Redesign SystemV (ZEN-3199)
        if services[0] == 'SYSTEMV':
            if services[1] in SYSV_EXIT_CODE:
                message = SYSV_EXIT_CODE.get(services[1])
            elif int(services[1]) in xrange(5, 99):
                message = 'Reserved for future LSB use'
            elif int(services[1]) in xrange(100, 149):
                message = 'Reserved for distribution use'
            elif int(services[1]) in xrange(150, 199):
                message = 'Reserved for application use'
            else:
                message = 'Reserved'

            if services[1] != '0':
                status_value = 0
                event_status = 'down'
                severity = cmd.severity

            event = {
                'device': cmd.deviceConfig.device,
                'component': cmd.component,
                'severity': severity,
                'eventClassKey': 'linux-service-status',
                'summary': 'OS Service is {}'.format(event_status),
                'message': 'Exit status: ' + message
            }

            # Mappings can only work if eventClass isn't set.
            if cmd.eventClass != ZenEventClasses.Unknown:
                event["eventClass"] = cmd.eventClass

            result.events.append(event)

            for dp in cmd.points:
                if 'status' in dp.id:
                    result.values.append((dp, status_value))

            return result

        # Continues code for SystemD and Upstart
        initService = SERVICE_MAP.get(services[0])
        if not initService:
            log.debug("Cannot parse OS services, init service is unknown!")
            return result

        services = services[1:]
        # regex_perf used for sysd where modeling/perf commands are different
        regex = initService.get('regex_perf') or initService.get('regex')
        functions = initService.get('functions')
        if functions:
            services = functions.get('monitoring')(services)

        # Get comp name over id (id does not have special chars like '@')
        for dp in cmd.points:
            if 'status' in dp.id:
                name = dp.data['id']
        # Look through services for service match
        for line in services:
            line = line.strip()
            match = regex.match(line)
            if not match:
                continue

            groupdict = match.groupdict()
            title = groupdict.get('title')
            if name != title:
                continue
            active_status = groupdict.get('active_status')
            status_string = active_status.split()[0]
            # Check if status is active or running
            if status_string not in ON_STATUS:
                status_value = 0    # STATUS OFF/INACTIVE
                severity = cmd.severity
                event_status = 'down'

            event = {
                'device': cmd.deviceConfig.device,
                'component': cmd.component,
                'severity': severity,
                'eventClassKey': 'linux-service-status',
                'summary': 'OS Service is {}'.format(event_status),
                'message': active_status
            }

            # Mappings can only work if eventClass isn't set.
            if cmd.eventClass != ZenEventClasses.Unknown:
                event["eventClass"] = cmd.eventClass

            # Send a event if down, else clear events
            result.events.append(event)
            break

        for dp in cmd.points:
            if 'status' in dp.id:
                result.values.append((dp, status_value))

        return result
