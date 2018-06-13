##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


"""
Systemd perf output('systemctl list-units -t service --all --no-page --no-legend | cut -d" " -f1 | xargs -n 1 systemctl status -l -n 0'):
    ...
    systemd-udev-trigger.service - udev Coldplug all Devices
       Loaded: loaded (/usr/lib/systemd/system/systemd-udev-trigger.service; static; vendor preset: disabled)
       Active: active (exited) since Tue 2016-02-02 12:47:58 UTC; 3 weeks 6 days ago
         Docs: man:udev(7)
               man:systemd-udevd.service(8)
      Process: 436 ExecStart=/usr/bin/udevadm trigger --type=devices --action=add (code=exited, status=0/SUCCESS)
      Process: 434 ExecStart=/usr/bin/udevadm trigger --type=subsystems --action=add (code=exited, status=0/SUCCESS)
     Main PID: 436 (code=exited, status=0/SUCCESS)
       Memory: 0B
       CGroup: /system.slice/systemd-udev-trigger.service
    systemd-udevd.service - udev Kernel Device Manager
       Loaded: loaded (/usr/lib/systemd/system/systemd-udevd.service; static; vendor preset: disabled)
       Active: active (running) since Tue 2016-02-02 12:47:59 UTC; 3 weeks 6 days ago
         Docs: man:systemd-udevd.service(8)
               man:udev(7)
     Main PID: 445 (systemd-udevd)
       Memory: 496.0K
       CGroup: /system.slice/systemd-udevd.service
               445 /usr/lib/systemd/systemd-udevd
    systemd-update-done.service - Update is Completed
       Loaded: loaded (/usr/lib/systemd/system/systemd-update-done.service; static; vendor preset: disabled)
       Active: inactive (dead)
    Condition: start condition failed at Tue 2016-02-02 12:48:04 UTC; 3 weeks 6 days ago
               none of the trigger conditions were met
         Docs: man:systemd-update-done.service(8)
    systemd-update-utmp-runlevel.service - Update UTMP about System Runlevel Changes
       Loaded: loaded (/usr/lib/systemd/system/systemd-update-utmp-runlevel.service; static; vendor preset: disabled)
       Active: inactive (dead) since Tue 2016-02-02 13:04:10 UTC; 3 weeks 6 days ago
         Docs: man:systemd-update-utmp.service(8)
               man:utmp(5)
      Process: 2547 ExecStart=/usr/lib/systemd/systemd-update-utmp runlevel (code=exited, status=0/SUCCESS)
     Main PID: 2547 (code=exited, status=0/SUCCESS)
    systemd-update-utmp.service - Update UTMP about System Boot/Shutdown
       Loaded: loaded (/usr/lib/systemd/system/systemd-update-utmp.service; static; vendor preset: disabled)
       Active: active (exited) since Tue 2016-02-02 12:48:05 UTC; 3 weeks 6 days ago
         Docs: man:systemd-update-utmp.service(8)
               man:utmp(5)
      Process: 629 ExecStart=/usr/lib/systemd/systemd-update-utmp reboot (code=exited, status=0/SUCCESS)
     Main PID: 629 (code=exited, status=0/SUCCESS)
       Memory: 0B
       CGroup: /system.slice/systemd-update-utmp.service
       display-manager.service
       Loaded: not-found (Reason: No such file or directory)
       Active: inactive (dead)
     kdump.service - Crash recovery kernel arming
       Loaded: loaded (/usr/lib/systemd/system/kdump.service; disabled; vendor preset: enabled)
       Active: failed (Result: exit-code) since Tue 2018-03-06 12:05:18 CST; 2 days ago
       Process: 32754 ExecStart=/usr/bin/kdumpctl start (code=exited, status=1/FAILURE)
       Main PID: 32754 (code=exited, status=1/FAILURE)
    ...


Systemd model output('for i in $(sudo systemctl list-units -t service --all
                --no-page --no-legend | sed /not-found/d | cut -d" " -f1) ;
                do echo "__SPLIT__" ;
                sudo systemctl show -p Names,Type,Description,LoadState,
                ActiveState,UnitFileState,MainPID,ConditionResult $i ; done'):
    ...
    Type=oneshot
    MainPID=0
    Names=iscsi-shutdown.service
    Description=Logout off all iSCSI sessions on shutdown
    LoadState=loaded
    ActiveState=active
    UnitFileState=static
    ConditionResult=yes
    __SPLIT__
    Type=oneshot
    MainPID=0
    Names=iscsi.service
    Description=Login and scanning of iSCSI devices
    LoadState=loaded
    ActiveState=inactive
    UnitFileState=enabled
    ConditionResult=no
    __SPLIT__
    Type=forking
    MainPID=0
    Names=iscsid.service
    Description=Open-iSCSI
    LoadState=loaded
    ActiveState=inactive
    UnitFileState=disabled
    ConditionResult=no
    __SPLIT__
    Type=forking
    MainPID=0
    Names=iscsiuio.service
    Description=iSCSI UserSpace I/O driver
    LoadState=loaded
    ActiveState=inactive
    UnitFileState=disabled
    ConditionResult=no
    __SPLIT__
    Type=oneshot
    MainPID=0
    Names=kdump.service
    Description=Crash recovery kernel arming
    LoadState=loaded
    ActiveState=inactive
    UnitFileState=disabled
    ConditionResult=no
    ...


Upstart output('initctl list'):

    ...
    upstart-udev-bridge start/running, process 557
    mountall-net stop/waiting
    nmbd start/running, process 1282
    passwd stop/waiting
    rc stop/waiting
    rsyslog start/running, process 1121
    startpar-bridge stop/waiting
    tty4 start/running, process 1159
    ureadahead-other stop/waiting
    apport start/running
    console-setup stop/waiting
    hwclock-save stop/waiting
    idmapd-mounting stop/waiting
    irqbalance start/running, process 1317
    plymouth-log stop/waiting
    pollinate stop/waiting
    rpcbind-boot stop/waiting
    smbd start/running, process 954
    systemd-logind start/running, process 1078
    tty5 start/running, process 1163
    statd start/running, process 721
    failsafe stop/waiting
    mountall.sh start/running
    resolvconf start/running
    atd start/running, process 1229
    dbus start/running, process 998
    docker start/running, process 958
    ...


Systemv output('ls -l /etc/rc${CURRENT_RUNLEVEL}.d/'):

    ...
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
    ...


"""


import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin


__doc__ = """os_service
Collect linux services information using appropriate init service command.
"""


RE_SYSTEMD_SERVICE_PERF = re.compile(
                            '(?P<title>[@\w\-\.:]+)\.service\s\-\s'          # service title
                            '(?P<description>.+)\s+'                         # description
                            'Loaded:\s(?P<loaded_status>\w.+\))\s+'          # loaded status
                            '(Drop-In:(?P<drop_in>\s/\w[\w./].+)\s+)?'       # optional Drop-In
                            'Active:\s+'
                            '(?P<active_status>\w+\s\([\w:\s-]+\)(\ssince.+ago)?)' # active status
                            '(.+Main\sPID:\s(?P<main_pid>\d+))?'             # optional sevicepid
                            '.*')
RE_SYSTEMD_SERVICE_MODEL = re.compile(
                                # sysd_type
                                'Type=(?P<sysd_type>\w+)\n'
                                # main_pid
                                'MainPID=(?P<main_pid>\d+)\n'
                                # title
                                'Names=(?P<title>[@\w\-\.:]+)\.service\n'
                                # description
                                'Description=(?P<description>.+)\n'
                                # load status
                                'LoadState=(?P<loaded_status>\w+)\n'
                                # active status
                                'ActiveState=(?P<active_status>\w+)\n'
                                # unit file state
                                'UnitFileState=(?P<unit_file_state>\w+)\n'
                                # condition
                                'ConditionResult=(?P<condition_result>\w+)')
RE_UPSTART_SERVICE = re.compile('(?P<title>[\w\-]+(\s\([\w\/]+\))?)\s'    # service title
                                '(?P<goal>([\w]+)?)/(?P<active_status>([\w]+)?)' # active status
                                '(.\sprocess\s(?P<main_pid>\d+))?')       # active status if exists
# Only links that start with 'S' are running in current runlevel
# Matches output of "ls -l /etc/rc${CURRENT_RUNLEVEL}.d/"
#   lrwxrwxrwx 1 root root 16 Oct 15  2009 K36mysqld -> ../init.d/mysqld
#   lrwxrwxrwx 1 root root 15 Oct 15  2009 S50snmpd -> ../init.d/snmpd
RE_SYSTEMV_SERVICE = re.compile(ur'S\d+[\w-]+\s->\s\.\./init\.d/(?P<title>.+)')


def systemd_processServices(results):
    # Parse results by __SPLIT__ to get data per service
    services = results.split("\n__SPLIT__\n")
    # Remove last new line character at the last index value of serivce
    services[-1] = services[-1][:-1]
    # return service without 'SYSTEMD' in first index
    return services[1:]


def systemd_getServices(services):
    """
    Build a list of services.
    The delimiter of a new service line is BLACK CIRCLE unicode char.
    """
    uServices = unicode(''.join(services), 'utf-8')
    # remove these unicode chars before we splitlines() and parse
    if re.match(ur'.*\u2514\u2500.*', uServices):
        uServices = re.sub(ur'\u2514\u2500', ' ', uServices)

    if re.match(ur'\u25cf', uServices):
        return re.sub(ur'\u25cf', '\n', uServices).splitlines()
    else:
        uServices = unicode('\n'.join(services), 'utf-8')
        return re.sub(r'\n([\s\w])', '\\1', uServices).splitlines()


def check_services_modeled(model_list, ignore_list, title):
    # Return False if service is not to be modeled
    for name in ignore_list:
        if re.match(name, title):
            return False

    if model_list:
        for name in model_list:
            if re.match(name, title):
                return True
        return False
    else:
        return None


def validate_modeling_regex(device, log):
    # Validate Regex and return valid expressions
    model_list, ignore_list = [], []

    zLinuxServicesModeled = getattr(device, 'zLinuxServicesModeled', [])

    # Make list for services to be modeled
    for name in zLinuxServicesModeled:
        try:
            re.compile(name)
            model_list.append(name)
        except:
            log.warn('Ignoring "{}" in zLinuxServicesModeled. '
                     'Invalid Regular Expression.'.format(name))

    # Make list for services to be ignored
    for name in getattr(device, 'zLinuxServicesNotModeled', []):
        try:
            re.compile(name)
            ignore_list.append(name)
        except:
            log.warn('Ignoring "{}" in zLinuxServicesNotModeled. '
                     'Invalid Regular Expression.'.format(name))

    return model_list, ignore_list

# Service Map is used for modeling and monitoring
SERVICE_MAP = {
    'SYSTEMD': {
        'regex': RE_SYSTEMD_SERVICE_MODEL,
        'regex_perf': RE_SYSTEMD_SERVICE_PERF,
        'functions': {
            'modeling': systemd_processServices,
            'monitoring': systemd_getServices,
        }
    },
    'UPSTART': {
        'regex': RE_UPSTART_SERVICE,
    },
    'SYSTEMV': {
        'regex': RE_SYSTEMV_SERVICE,
    },
    'UNKNOWN': None
}


class os_service(LinuxCommandPlugin):
    requiredProperties = ('zLinuxServicesModeled', 'zLinuxServicesNotModeled', 'zLinuxModelAllActiveServices')
    deviceProperties = LinuxCommandPlugin.deviceProperties + requiredProperties
    command = ('export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin; '
               'if command -v systemctl >/dev/null 2>&1; then '
                'echo "SYSTEMD"; '
                'for i in $(sudo systemctl list-units -t service --all --no-page --no-legend | sed /not-found/d | cut -d" " -f1) ; '
                 'do echo "__SPLIT__" ; '
                 'sudo systemctl show -p Names,Type,Description,LoadState,ActiveState,UnitFileState,MainPID,ConditionResult $i ; '
                 'done; '
               'elif command -v initctl >/dev/null 2>&1; then '
                'echo "UPSTART"; '
                'sudo initctl list 2>&1 || true ; '
                'echo "SYSV_SERVICES"; '
                'sudo ls -l /etc/rc$(/sbin/runlevel | awk \'{print $2}\').d/ 2>&1 || true; '
               'elif command -v service >/dev/null 2>&1; then '
                'echo "SYSTEMV"; '
                'sudo ls -l /etc/rc$(/sbin/runlevel | awk \'{print $2}\').d/ 2>&1 || true; '
               'else '
                'echo "UNKNOWN"; '
                'exit 127; '
               'fi')

    compname = ''
    relname = 'linuxServices'
    modname = 'ZenPacks.zenoss.LinuxMonitor.LinuxService'

    def populateRelMap(self, rm, model_list, ignore_list, init_system,
                       services, regex, device, log):
        for line in services:
            line = line.strip()
            # Upstart models both sysv and upstart services (ZPS-3478)
            if line == "SYSV_SERVICES":
                regex = SERVICE_MAP["SYSTEMV"]["regex"]
                init_system = "SYSTEMV"
            match = regex.search(line)
            if match:
                groupdict = match.groupdict()
                title = groupdict.get('title')
                # Check zProperties for services to be modeled
                model_override = check_services_modeled(model_list,
                                                        ignore_list,
                                                        title)

                # Service is in zLinuxServicesModeled (override)
                if model_override is True:
                    # Service will end up modeled.
                    pass

                # Service is in zLinuxServicesNotModeled (override)
                elif model_override is False:
                    # Service will not be modeled.
                    continue

                # Service not in zLinuxServicesModeled or
                # zLinuxServicesNotModeled
                else:
                    if init_system == "UPSTART":
                        expected_running = upstart_expected_running(device,
                                                                    groupdict)
                    elif init_system == "SYSTEMD":
                        expected_running = sysd_expected_running(device,
                                                                 groupdict)
                    else:
                        # SYSTEMV requires no addtional processing beyond regex
                        expected_running = True

                    if not expected_running:
                        continue

                # Create relmaps
                om = self.objectMap()
                om.id = 'service_' + self.prepId(title)
                om.title = title
                om.init_system = init_system
                om.description = groupdict.get('description', '').strip()
                rm.append(om)
            else:
                log.debug("Unmapped in populateRelMap(): %s", line)
                continue

    def process(self, device, results, log):
        log.info("Processing the OS Service info for device %s", device.id)
        rm = self.relMap()
        # Validate regex and log warning message for invalid regex
        model_list, ignore_list = validate_modeling_regex(device, log)
        services = results.splitlines()
        init_system = services[0]
        initService = SERVICE_MAP.get(init_system)
        if initService:
            services = services[1:]
            regex = initService.get('regex')
            functions = initService.get('functions')
            if functions:
                services = functions.get('modeling')(results)
            self.populateRelMap(rm, model_list, ignore_list, init_system,
                                services, regex, device, log)
            log.debug("Init service: %s, Relationship: %s", initService,
                      rm.relname)
        else:
            log.info("Cannot parse OS services, init service is unknown!")

        return [rm]


def upstart_expected_running(device, groupdict):
    """Return True if service in groupdict is expected to be running."""
    active_status = groupdict.get('active_status', '')
    goal = groupdict.get('goal', '')

    # Higher level "enabled" concept.
    enabled = (goal == "start")

    # Higher level "active" concept.
    active = (active_status == "running")

    model_all_active_services = getattr(
        device, "zLinuxModelAllActiveServices", False)

    if enabled or (active and model_all_active_services):
        return True

    return False


def sysd_expected_running(device, groupdict):
    """Return True if service in groupdict is expected to be running."""
    unit_file_state = groupdict.get('unit_file_state', None)
    active_status = groupdict.get('active_status', '')
    sysd_type = groupdict.get('sysd_type', '')
    condition_result = groupdict.get('condition_result', '')

    # Not expected to be running if any of these conditions are true.
    if sysd_type == "oneshot" or condition_result == "no":
        return False

    # Higher level "enabled" concept.
    enabled = unit_file_state in ("enabled", "enabled-runtime")

    # Higher level "active" concept.
    active = (active_status in ("active", "activating", "reloading"))

    model_all_active_services = getattr(
        device, "zLinuxModelAllActiveServices", False)

    if enabled or (active and model_all_active_services):
        return True

    return False
