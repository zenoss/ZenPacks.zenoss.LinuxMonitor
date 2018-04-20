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
    total 288
    lrwxrwxrwx 1 root root 17 Oct  1  2009 K00ipmievd -> ../init.d/ipmievd
    lrwxrwxrwx 1 root root 17 Oct  1  2009 K01dnsmasq -> ../init.d/dnsmasq
    lrwxrwxrwx 1 root root 24 Oct  1  2009 K02avahi-dnsconfd -> ../init.d/avahi-dnsconfd
    lrwxrwxrwx 1 root root 24 Oct  1  2009 K02NetworkManager -> ../init.d/NetworkManager
    lrwxrwxrwx 1 root root 16 Oct  1  2009 K05conman -> ../init.d/conman
    lrwxrwxrwx 1 root root 19 Oct  1  2009 K05saslauthd -> ../init.d/saslauthd
    lrwxrwxrwx 1 root root 17 Oct  1  2009 K05wdaemon -> ../init.d/wdaemon
    lrwxrwxrwx 1 root root 16 Oct  1  2009 K10psacct -> ../init.d/psacct
    lrwxrwxrwx 1 root root 15 Oct  1  2009 K15httpd -> ../init.d/httpd
    lrwxrwxrwx 1 root root 13 Oct  1  2009 K20nfs -> ../init.d/nfs
    lrwxrwxrwx 1 root root 14 Oct  1  2009 K24irda -> ../init.d/irda
    lrwxrwxrwx 1 root root 13 Oct  1  2009 K35smb -> ../init.d/smb
    lrwxrwxrwx 1 root root 19 Oct  1  2009 K35vncserver -> ../init.d/vncserver
    lrwxrwxrwx 1 root root 17 Oct  1  2009 K35winbind -> ../init.d/winbind
    lrwxrwxrwx 1 root root 16 Oct 15  2009 K36mysqld -> ../init.d/mysqld
    lrwxrwxrwx 1 root root 20 Oct  1  2009 K50netconsole -> ../init.d/netconsole
    lrwxrwxrwx 1 root root 19 Oct 15  2009 K50snmptrapd -> ../init.d/snmptrapd
    lrwxrwxrwx 1 root root 20 Oct  1  2009 K69rpcsvcgssd -> ../init.d/rpcsvcgssd
    lrwxrwxrwx 1 root root 16 Oct  1  2009 K73ypbind -> ../init.d/ypbind
    lrwxrwxrwx 1 root root 14 Oct 15  2009 K74ipmi -> ../init.d/ipmi
    lrwxrwxrwx 1 root root 14 Oct  1  2009 K74nscd -> ../init.d/nscd
    lrwxrwxrwx 1 root root 15 Oct  1  2009 K80kdump -> ../init.d/kdump
    lrwxrwxrwx 1 root root 15 Oct  1  2009 K85mdmpd -> ../init.d/mdmpd
    lrwxrwxrwx 1 root root 20 Oct  1  2009 K87multipathd -> ../init.d/multipathd
    lrwxrwxrwx 1 root root 24 Oct  1  2009 K88wpa_supplicant -> ../init.d/wpa_supplicant
    lrwxrwxrwx 1 root root 14 Oct  1  2009 K89dund -> ../init.d/dund
    lrwxrwxrwx 1 root root 18 Oct  1  2009 K89netplugd -> ../init.d/netplugd
    lrwxrwxrwx 1 root root 14 Oct  1  2009 K89pand -> ../init.d/pand
    lrwxrwxrwx 1 root root 15 Oct  1  2009 K89rdisc -> ../init.d/rdisc
    lrwxrwxrwx 1 root root 14 Oct  1  2009 K91capi -> ../init.d/capi
    lrwxrwxrwx 1 root root 23 Oct  1  2009 S00microcode_ctl -> ../init.d/microcode_ctl
    lrwxrwxrwx 1 root root 22 Oct  1  2009 S02lvm2-monitor -> ../init.d/lvm2-monitor
    lrwxrwxrwx 1 root root 25 Oct  1  2009 S04readahead_early -> ../init.d/readahead_early
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S05kudzu -> ../init.d/kudzu
    lrwxrwxrwx 1 root root 18 Oct  1  2009 S06cpuspeed -> ../init.d/cpuspeed
    lrwxrwxrwx 1 root root 19 Apr 11 08:18 S08ip6tables -> ../init.d/ip6tables
    lrwxrwxrwx 1 root root 18 Apr 11 08:17 S08iptables -> ../init.d/iptables
    lrwxrwxrwx 1 root root 18 Oct  1  2009 S08mcstrans -> ../init.d/mcstrans
    lrwxrwxrwx 1 root root 14 Oct  1  2009 S09isdn -> ../init.d/isdn
    lrwxrwxrwx 1 root root 17 Oct  1  2009 S10network -> ../init.d/network
    lrwxrwxrwx 1 root root 16 Oct  1  2009 S11auditd -> ../init.d/auditd
    lrwxrwxrwx 1 root root 21 Oct  1  2009 S12restorecond -> ../init.d/restorecond
    lrwxrwxrwx 1 root root 16 Oct  1  2009 S12syslog -> ../init.d/syslog
    lrwxrwxrwx 1 root root 20 Oct  1  2009 S13irqbalance -> ../init.d/irqbalance
    lrwxrwxrwx 1 root root 17 Oct  1  2009 S13portmap -> ../init.d/portmap
    lrwxrwxrwx 1 root root 17 Oct  1  2009 S14nfslock -> ../init.d/nfslock
    lrwxrwxrwx 1 root root 19 Oct  1  2009 S15mdmonitor -> ../init.d/mdmonitor
    lrwxrwxrwx 1 root root 19 Oct  1  2009 S18rpcidmapd -> ../init.d/rpcidmapd
    lrwxrwxrwx 1 root root 17 Oct  1  2009 S19rpcgssd -> ../init.d/rpcgssd
    lrwxrwxrwx 1 root root 22 Oct  2  2009 S19vmware-tools -> ../init.d/vmware-tools
    lrwxrwxrwx 1 root root 20 Oct  1  2009 S22messagebus -> ../init.d/messagebus
    lrwxrwxrwx 1 root root 24 Oct  1  2009 S23setroubleshoot -> ../init.d/setroubleshoot
    lrwxrwxrwx 1 root root 19 Oct  1  2009 S25bluetooth -> ../init.d/bluetooth
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S25netfs -> ../init.d/netfs
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S25pcscd -> ../init.d/pcscd
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S26acpid -> ../init.d/acpid
    lrwxrwxrwx 1 root root 14 Oct  1  2009 S26apmd -> ../init.d/apmd
    lrwxrwxrwx 1 root root 19 Oct  1  2009 S26haldaemon -> ../init.d/haldaemon
    lrwxrwxrwx 1 root root 14 Oct  1  2009 S26hidd -> ../init.d/hidd
    lrwxrwxrwx 1 root root 20 Oct 15  2009 S26lm_sensors -> ../init.d/lm_sensors
    lrwxrwxrwx 1 root root 16 Oct  1  2009 S28autofs -> ../init.d/autofs
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S50hplip -> ../init.d/hplip
    lrwxrwxrwx 1 root root 15 Oct 15  2009 S50snmpd -> ../init.d/snmpd
    lrwxrwxrwx 1 root root 14 Oct  1  2009 S55sshd -> ../init.d/sshd
    lrwxrwxrwx 1 root root 14 Oct  1  2009 S56cups -> ../init.d/cups
    lrwxrwxrwx 1 root root 20 Oct  1  2009 S56rawdevices -> ../init.d/rawdevices
    lrwxrwxrwx 1 root root 16 Oct  1  2009 S56xinetd -> ../init.d/xinetd
    lrwxrwxrwx 1 root root 14 Oct 15  2009 S58ntpd -> ../init.d/ntpd
    lrwxrwxrwx 1 root root 18 Oct  1  2009 S80sendmail -> ../init.d/sendmail
    lrwxrwxrwx 1 root root 13 Oct  1  2009 S85gpm -> ../init.d/gpm
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S90crond -> ../init.d/crond
    lrwxrwxrwx 1 root root 13 Oct  1  2009 S90xfs -> ../init.d/xfs
    lrwxrwxrwx 1 root root 17 Oct  1  2009 S95anacron -> ../init.d/anacron
    lrwxrwxrwx 1 root root 13 Oct  1  2009 S95atd -> ../init.d/atd
    lrwxrwxrwx 1 root root 15 Oct 15  2009 S95jexec -> ../init.d/jexec
    lrwxrwxrwx 1 root root 25 Oct  1  2009 S96readahead_later -> ../init.d/readahead_later
    lrwxrwxrwx 1 root root 15 Oct  1  2009 S97rhnsd -> ../init.d/rhnsd
    lrwxrwxrwx 1 root root 22 Oct  1  2009 S97yum-updatesd -> ../init.d/yum-updatesd
    lrwxrwxrwx 1 root root 22 Oct  1  2009 S98avahi-daemon -> ../init.d/avahi-daemon
    lrwxrwxrwx 1 root root 19 Oct  1  2009 S99firstboot -> ../init.d/firstboot
    lrwxrwxrwx 1 root root 11 Oct  1  2009 S99local -> ../rc.local
    lrwxrwxrwx 1 root root 16 Oct  1  2009 S99smartd -> ../init.d/smartd
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
        self.assertEqual(len(rm[0].maps), 51)

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
        self.device.zLinuxServicesModeled = ['^readahead.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 0)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 3)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 2)

    def test_zLinuxServicesNotModeled(self):
        # Test with default/blank value
        self.device.zLinuxServicesNotModeled = []
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 51)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesNotModeled = ['^abrt.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 2)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 21)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 51)

        # Test with UPSTART services with regex
        self.device.zLinuxServicesNotModeled = ['^tty.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 15)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 51)

        # Test with SYSTEMD services with regex
        self.device.zLinuxServicesNotModeled = ['^readahead.*']
        rm = self.plugin.process(self.device, SYSTEMD_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 7)
        rm = self.plugin.process(self.device, UPSTART_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 18)
        rm = self.plugin.process(self.device, SYSTEMV_OUTPUT, LOG)
        self.assertEqual(len(rm[0].maps), 49)
