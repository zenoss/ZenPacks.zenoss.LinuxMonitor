##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging
import unittest

from Products.DataCollector.DeviceProxy import DeviceProxy
from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.os_service \
                                                        import os_service

SYSTEMD_OUTPUT = """SYSTEMD\n\xe2\x97\x8f abrt-ccpp.service - Install ABRT coredump hook
   Loaded: loaded (/usr/lib/systemd/system/abrt-ccpp.service; enabled; vendor preset: enabled)
   Active: active (exited) since Tue 2017-09-05 14:52:45 CDT; 6 months 0 days ago
  Process: 762 ExecStart=/usr/sbin/abrt-install-ccpp-hook install (code=exited, status=0/SUCCESS)
 Main PID: 762 (code=exited, status=0/SUCCESS)
   CGroup: /system.slice/abrt-ccpp.service
\n\xe2\x97\x8f abrt-oops.service - ABRT kernel log watcher
   Loaded: loaded (/usr/lib/systemd/system/abrt-oops.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2017-09-05 14:52:44 CDT; 6 months 0 days ago
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

SYSTEMV_OUTPUT = """SYSTEMV
    htcacheclean is stopped
    httpd is stopped
    ip6tables: Firewall is not running.
    IPsec stopped
    iptables: Firewall is not running.
    irqbalance (pid  1163) is running...
    iscsi is stopped
    iscsid is stopped
    Kdump is not operational
    lldpad (pid  1200) is running...
    lvmetad is stopped
    mdmonitor is stopped
    messagebus (pid  1240) is running...
    multipathd is stopped
    mysqld is stopped
    netconsole module not loaded
    Configured devices:
    lo Auto_eth0
    Currently active devices:
    lo eth0
    NetworkManager (pid  1251) is running...
    rpc.svcgssd is stopped
    rpc.mountd is stopped
    nfsd is stopped
    rpc.rquotad is stopped
    rpc.statd (pid  1270) is running...
    nscd is stopped
    """

LOG = logging.getLogger("zen.testcases")


class ServiceModelerTests(unittest.TestCase):
    def setUp(self):
        super(ServiceModelerTests, self).setUp()

        self.plugin = os_service()
        self.device = DeviceProxy()
        self.device.id = "test-LinuxService"
        self.device.zLinuxServicesModeled = []
        self.device.zLinuxServicesNotModeled = []

    def test_zLinuxServicesModeled(self):
        # Test with default/blank value for systemd, upstart and systemv
        self.device.zLinuxServicesModeled = []
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesModeled = ['^abrt.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 5)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)

        # Test with UPSTART services with regex
        self.device.zLinuxServicesModeled = ['^tty.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 6)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesModeled = ['^rpc.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 4)

    def test_zLinuxServicesNotModeled(self):
        # Test with default/blank value
        self.device.zLinuxServicesNotModeled = []
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesNotModeled = ['^abrt.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 2)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)

        # Test with UPSTART services with regex
        self.device.zLinuxServicesNotModeled = ['^tty.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 15)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesNotModeled = ['^rpc.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 17)
