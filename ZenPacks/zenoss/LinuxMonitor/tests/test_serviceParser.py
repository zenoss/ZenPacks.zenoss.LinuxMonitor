##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
from pprint import pformat
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.CommandParser import ParsedResults

from ZenPacks.zenoss.LinuxMonitor.parsers.linux.service import service

SYSTEMD_OUTPUT = """
SYSTEMD
auditd.service                         loaded    active   running Security Auditing Service
brandbot.service                       loaded    inactive dead    Flexible Branding Service
cpupower.service                       loaded    inactive dead    Configure CPU power related settings
crond.service                          loaded    active   running Command Scheduler
dbus.service                           loaded    active   running D-Bus System Message Bus
display-manager.service                not-found inactive dead    display-manager.service
dm-event.service                       loaded    active   running Device-mapper event daemon
dracut-shutdown.service                loaded    inactive dead    Restore /run/initramfs
emergency.service                      loaded    inactive dead    Emergency Shell
exim.service                           not-found inactive dead    exim.service
""".strip()

UPSTART_OUTPUT = """UPSTART
    rc stop/waiting
    tty (/dev/tty3) start/running, process 1474
    tty (/dev/tty2) start/running, process 1472
    tty (/dev/tty1) start/running, process 1470
    tty (/dev/tty6) start/running, process 1480
    tty (/dev/tty5) start/running, process 1478
    tty (/dev/tty4) start/running, process 1476
    plymouth-shutdown stop/waiting
    control-alt-delete stop/waiting
    readahead-collector stop/waiting
    kexec-disable stop/waiting
    quit-plymouth stop/waiting
    rcS stop/waiting
    prefdm stop/waiting
    init-system-dbus stop/waiting
    readahead stop/waiting
    splash-manager stop/waiting
    start-ttys stop/waiting
    readahead-disable-services stop/waiting
    rcS-sulogin stop/waiting
    serial stop/waiting"""

LOG = logging.getLogger("zen.testcases")


class Object(object):

    def __init__(self, **kw):
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return pformat(dict(
            (attr, getattr(self, attr))
            for attr in dir(self)
            if not attr.startswith('__')
        ))


class ServiceParserTests(BaseTestCase):
    def setUp(self):
        self.cmd = Object(**{
            "deviceConfig":   Object(**{
                "device": "ParserDevice",
            }),
            "component": "",
            "eventClass": "/Status",
            "severity":       3,
            "points": [
                Object(**{
                    "id": "status",
                    "data": {}
                }),
            ]
        })
        self.cmd.result = Object(**{"exitCode": 0,
                                    "output": ""})

    def test_SystemDEvents(self):
        self.cmd.result.output = SYSTEMD_OUTPUT

        # Test Event is Down
        result = ParsedResults()
        self.cmd.component = 'brandbot'
        self.cmd.points[0]['data']['id'] = 'brandbot'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')

        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'auditd'
        self.cmd.points[0]['data']['id'] = 'auditd'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is up')

    def test_UpstartEvents(self):
        self.cmd.result.output = UPSTART_OUTPUT

        # Test Event is Down
        result = ParsedResults()
        self.cmd.component = 'plymouth-shutdown'
        self.cmd.points[0]['data']['id'] = 'plymouth-shutdown'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')

        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'tty (_dev_tty6)'
        self.cmd.points[0]['data']['id'] = 'tty (/dev/tty6)'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is up')

    def test_SystemVEvents(self):
        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n0\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is up')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is running or service is OK')

        # Test Event is Down with exit code 1
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n1\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is dead and /var/run pid file exists')

        # Test Event is Down with exit code 2
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n2\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is dead and /var/lock lock file exists')

        # Test Event is Down with exit code 3
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n3\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is not running')

        # Test Event is Down with exit code 4
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n4\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program or service status is unknown')

        # Test Event is Down with exit code 10
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n10\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for future LSB use')

        # Test Event is Down with exit code 140
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n140\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for distribution use')

        # Test Event is Down with exit code 155
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n155\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for application use')


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(ServiceParserTests))

    return suite
