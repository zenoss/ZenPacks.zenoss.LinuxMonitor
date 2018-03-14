##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


"""
Systemd output('systemctl list-units -t service --all --no-page --no-legend | cut -d" " -f1 | xargs -n 1 systemctl status -l -n 0'):
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


Systemv output('service --status-all'):

    ...
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
    ...


"""


import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin


__doc__ = """os_service
Collect linux services information using appropriate init service command.
"""


RE_SYSTEMD_SERVICE = re.compile(
                        '(?P<title>[@\w\-\.:]+)\.service\s\-\s'          # service title
                        '(?P<description>.+)\s+'                         # description
                        'Loaded:\s(?P<loaded_status>\w.+\))\s+'          # loaded status
                        '(Drop-In:(?P<drop_in>\s/\w[\w./].+)\s+)?'       # optional Drop-In
                        'Active:\s+'
                        '(?P<active_status>\w+\s\([\w:\s-]+\)(\ssince.+ago)?)' # active status
                        '(.+Main\sPID:\s(?P<main_pid>\d+))?'             # optional sevicepid
                        '.*')
RE_UPSTART_SERVICE = re.compile('(?P<title>[\w\-]+(\s\([\w\/]+\))?)\s'   # service title
                                '(?P<active_status>[\w\/]+)'             # active status
                                '(.\sprocess\s(?P<main_pid>\d+))?')      # active status if exists
RE_SYSTEMV_SERVICE = re.compile('(?P<title>[A-Za-z0-9_\-\.\s:]+)'
                                '((\s|:)\(pid\s+(?P<main_pid>\d+)\))?'
                                '\sis\s(?P<active_status>[\w\s]+)')


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

    for name in model_list:
        if re.match(name, title):
            return True
    return False


def validate_modeling_regex(device, log):
    # Validate Regex and return valid expressions
    model_list, ignore_list = [], []

    zLinuxServicesModeled = getattr(device, 'zLinuxServicesModeled', [])
    # Regex '.*' or empty list will model all services by default
    if not len(zLinuxServicesModeled):
        model_list.append('.*')
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


SERVICE_MAP = {
    'SYSTEMD': {
        'regex': RE_SYSTEMD_SERVICE,
        'functions': {
            'services': systemd_getServices,
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
    requiredProperties = ('zLinuxServicesModeled', 'zLinuxServicesNotModeled')
    deviceProperties = LinuxCommandPlugin.deviceProperties + requiredProperties
    command = ('export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin; '
               'if command -v systemctl >/dev/null 2>&1; then '
                'echo "SYSTEMD"; '
                'sudo systemctl list-units -t service --all --no-page --no-legend | sed /not-found/d | cut -d" " -f1 | xargs -n 1 sudo systemctl status -l -n 0 2>&1 || true; '
               'elif command -v initctl >/dev/null 2>&1; then '
                'echo "UPSTART"; '
                'sudo initctl list 2>&1 || true ; '
               'elif command -v service >/dev/null 2>&1; then '
                'echo "SYSTEMV"; '
                'sudo service --status-all 2>&1 || true; '
               'else '
                'echo "UNKNOWN"; '
                'exit 127; '
               'fi')

    compname = ''
    relname = 'linuxServices'
    modname = 'ZenPacks.zenoss.LinuxMonitor.LinuxService'

    def populateRelMap(self, rm, model_list, ignore_list, services, regex,
                       log):
        title_list = []
        for line in services:
            line = line.strip()
            match = regex.match(line)
            if match:
                groupdict = match.groupdict()
                title = groupdict.get('title')

                # Check zProperties for services to be modeled
                if not check_services_modeled(model_list, ignore_list, title):
                    continue

                # For SYSTEMD, only model services that are loaded
                loaded_status_string = groupdict.get('loaded_status', '')
                if loaded_status_string:
                    loaded_status = loaded_status_string.strip().split()[0]
                    if loaded_status != 'loaded':
                        continue

                # Check for duplicates (systemV shows duplicates e.g. Firewall)
                if title in title_list:
                    continue

                # create relmaps
                om = self.objectMap()
                om.id = self.prepId(title)
                om.title = title
                om.description = groupdict.get('description', '').strip()
                rm.append(om)
                # Add service to title_list to check for duplicates later
                title_list.append(title)
            else:
                log.debug("Unmapped in populateRelMap(): %s", line)
                continue

    def process(self, device, results, log):
        log.info("Processing the OS Service info for device %s", device.id)
        rm = self.relMap()
        # validate regex and log warning message for invalid regex
        model_list, ignore_list = validate_modeling_regex(device, log)
        services = results.splitlines()
        initService = SERVICE_MAP.get(services[0])
        if initService:
            services = services[1:]
            regex = initService.get('regex')
            functions = initService.get('functions')
            if functions:
                services = functions.get('services')(services)
            self.populateRelMap(rm, model_list, ignore_list,
                                services, regex, log)
            log.debug("Init service: %s, Relationship: %s", initService,
                      rm.relname)
        else:
            log.info("Can not parse OS services, init service is unknown!")

        return [rm]
