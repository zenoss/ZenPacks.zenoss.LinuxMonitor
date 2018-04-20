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

SYSTEMD_OUTPUT = """SYSTEMD\n\xe2\x97\x8f abrt-ccpp.service - Install ABRT coredump hook
   Loaded: loaded (/usr/lib/systemd/system/abrt-ccpp.service; enabled; vendor preset: enabled)
   Active: active (exited) since Tue 2017-09-05 14:52:45 CDT; 6 months 0 days ago
  Process: 762 ExecStart=/usr/sbin/abrt-install-ccpp-hook install (code=exited, status=0/SUCCESS)
 Main PID: 762 (code=exited, status=0/SUCCESS)
   CGroup: /system.slice/abrt-ccpp.service
\n\xe2\x97\x8f abrt-oops.service - ABRT kernel log watcher
   Loaded: loaded (/usr/lib/systemd/system/abrt-oops.service; enabled; vendor preset: enabled)
   Active: inactive (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
 Main PID: 764 (abrt-watch-log)
   CGroup: /system.slice/abrt-oops.service
           \xe2\x94\x94\xe2\x94\x80764 /usr/bin/abrt-watch-log -F BUG: WARNING: at WARNING: CPU: INFO: possible recursive locking detected ernel BUG at list_del corruption list_add corruption do_IRQ: stack overflow: ear stack overflow (cur: eneral protection fault nable to handle kernel ouble fault: RTNL: assertion failed eek! page_mapcount(page) went negative! adness at NETDEV WATCHDOG ysctl table check failed : nobody cared IRQ handler type mismatch Machine Check Exception: Machine check events logged divide error: bounds: coprocessor segment overrun: invalid TSS: segment not present: invalid opcode: alignment check: stack segment: fpu exception: simd exception: iret exception: /var/log/messages -- /usr/bin/abrt-dump-oops -xtD
\n\xe2\x97\x8f abrt-vmcore.service - Harvest vmcores for ABRT
   Loaded: loaded (/usr/lib/systemd/system/abrt-vmcore.service; enabled; vendor preset: enabled)
   Active: inactive (dead)
Condition: start condition failed at Tue 2018-03-06 12:04:12 CST; 1 day 5h ago
           ConditionDirectoryNotEmpty=/var/crash was not met
\n\xe2\x97\x8f abrt-xorg.service - ABRT Xorg log watcher
   Loaded: loaded (/usr/lib/systemd/system/abrt-xorg.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
 Main PID: 763 (abrt-watch-log)
   CGroup: /system.slice/abrt-xorg.service
           \xe2\x94\x94\xe2\x94\x80763 /usr/bin/abrt-watch-log -F Backtrace /var/log/Xorg.0.log -- /usr/bin/abrt-dump-xorg -xD
\n\xe2\x97\x8f abrtd.service - ABRT Automated Bug Reporting Tool
   Loaded: loaded (/usr/lib/systemd/system/abrtd.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
 Main PID: 761 (abrtd)
   CGroup: /system.slice/abrtd.service
           \xe2\x94\x94\xe2\x94\x80761 /usr/sbin/abrtd -d -s
\n\xe2\x97\x8f accounts-daemon.service - Accounts Service
   Loaded: loaded (/usr/lib/systemd/system/accounts-daemon.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
 Main PID: 696 (accounts-daemon)
   CGroup: /system.slice/accounts-daemon.service
           \xe2\x94\x94\xe2\x94\x80696 /usr/libexec/accounts-daemon
\n\xe2\x97\x8f alsa-restore.service - Save/Restore Sound Card State
   Loaded: loaded (/usr/lib/systemd/system/alsa-restore.service; static; vendor preset: disabled)
   Active: inactive (dead)
Condition: start condition failed at Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
           ConditionPathExists=!/etc/alsa/state-daemon.conf was not met
\n\xe2\x97\x8f alsa-state.service - Manage Sound Card State (restore and store)
   Loaded: not-found (/usr/lib/systemd/system/alsa-state.service; static; vendor preset: disabled)
   Active: active (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
 Main PID: 703 (alsactl)
   CGroup: /system.slice/alsa-state.service
           \xe2\x94\x94\xe2\x94\x80703 /usr/sbin/alsactl -s -n 19 -c -E ALSA_CONFIG_PATH=/etc/alsa/alsactl.conf --initfile=/lib/alsa/init/00main rdaemon
Unit apparmor.service could not be found."""

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
        self.cmd.component = 'abrt-oops'
        self.cmd.points[0]['data']['id'] = 'abrt-oops'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')

        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'abrt-ccpp'
        self.cmd.points[0]['data']['id'] = 'abrt-ccpp'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is up')

    def test_UpstartEvents(self):
        self.cmd.result.output = UPSTART_OUTPUT

        # Test Event is Down
        result = ParsedResults()
        self.cmd.component = 'plymouth-shutdown'
        self.cmd.points[0]['data']['id'] = 'plymouth-shutdown'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')

        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'tty (_dev_tty6)'
        self.cmd.points[0]['data']['id'] = 'tty (/dev/tty6)'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is up')

    def test_SystemVEvents(self):
        # Test Event is Up
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n0\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is up')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is running or service is OK')

        # Test Event is Down with exit code 1
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n1\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is dead and /var/run pid file exists')

        # Test Event is Down with exit code 2
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n2\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is dead and /var/lock lock file exists')

        # Test Event is Down with exit code 3
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n3\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program is not running')

        # Test Event is Down with exit code 4
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n4\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'program or service status is unknown')

        # Test Event is Down with exit code 10
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n10\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for future LSB use')

        # Test Event is Down with exit code 140
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n140\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for distribution use')

        # Test Event is Down with exit code 155
        result = ParsedResults()
        self.cmd.component = 'test_service'
        self.cmd.points[0]['data']['id'] = 'test_service'
        self.cmd.result.output = 'SYSTEMV\n155\n'
        service().processResults(self.cmd, result)
        self.assertEqual(result.events[0]['summary'], 'OS Service is down')
        self.assertEqual(result.events[0]['message'], 'Exit status: ' +
                         'Reserved for application use')


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(ServiceParserTests))

    return suite
