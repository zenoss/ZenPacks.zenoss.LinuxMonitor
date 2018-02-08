##############################################################################
#
# Copyright (C) Zenoss, Inc. 2009-2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


__doc__ = """ifconfig
ifconfig maps a linux ifconfig command to the interfaces relation.
"""

import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

speedPattern = re.compile(r'(\d+)\s*[gm]bps', re.I)


def parseDmesg(dmesg, relMap):
    """
    parseDmesg to get interface speed.
    """
    for line in dmesg.splitlines():
        speedMatch = speedPattern.search(line)
        if speedMatch:
            for objMap in relMap.maps:
                if objMap.interfaceName in line:
                    if 'Gbps' in speedMatch.group(0):
                        objMap.speed = int(speedMatch.group(1)) * 1e9
                    else:
                        objMap.speed = int(speedMatch.group(1)) * 1e6
                    break
    return relMap


def parseNetSpeed(netspeed, relMap):
    """Add speed to objMaps in relMap.

    netspeed is result of "head /sys/class/net/*/speed 2>&1".

    Example netspeed content:

        ==> /sys/class/net/docker0/speed <==
        head: error reading '/sys/class/net/docker0/speed': Invalid argument

        ==> /sys/class/net/eth0/speed <==
        10000

        ==> /sys/class/net/lo/speed <==
        head: error reading '/sys/class/net/lo/speed': Invalid argument

        ==> /sys/class/net/tun0/speed <==
        10

    """
    ifname = None
    ifname_matcher = re.compile(r'^==> /sys/class/net/([^/]+)/speed <==$').match
    speed_matcher = re.compile(r'^(\d+)$').match
    speeds = {}

    for line in netspeed.splitlines():
        ifname_match = ifname_matcher(line)
        if ifname_match:
            ifname = ifname_match.group(1)
            continue

        if ifname:
            speed_match = speed_matcher(line)
            if speed_match:
                speeds[ifname] = int(speed_match.group(1)) * 1e6

        # Avoid accidental capture of wrong speed later in the file.
        ifname = None

    for objmap in relMap.maps:
        if objmap.interfaceName in speeds:
            objmap.speed = speeds[objmap.interfaceName]

    return relMap


class interfaces(LinuxCommandPlugin):

    compname = "os"
    relname = "interfaces"
    modname = "Products.ZenModel.IpInterface"

    deviceProperties = LinuxCommandPlugin.deviceProperties + (
        'zInterfaceMapIgnoreNames',
        'zInterfaceMapIgnoreTypes',
        )

    # echo __COMMAND__ is used to delimit the results
    command = 'export PATH=$PATH:/sbin:/usr/sbin; \
               if which ip >/dev/null 2>&1; then \
                   echo "### ip addr output"; ip addr; \
               elif which ifconfig >/dev/null 2>&1; then \
                   ifconfig -a; \
               else \
                   echo "No ifconfig or ip utilities were found."; exit 127; \
               fi \
               && echo __COMMAND__ \
               && (/bin/dmesg || sudo -n /bin/dmesg || true) 2> /dev/null \
               && echo __COMMAND__ \
               && head /sys/class/net/*/speed 2>&1'

    # variables for ifconfig
    ifstart = re.compile(r"^(\S+?):?\s+")
    oldiftype = re.compile(r"^\S+\s+Link encap:(.+)HWaddr (\S+)"
                           r"|^\S+\s+Link encap:(.+)")
    v4addr = re.compile(r"inet addr:(\S+).*Mask:(\S+)"
                        r"|inet\s+(\S+)\s+netmask\s+(\S+)")
    v6addr = re.compile(r"inet6 addr: (\S+).*"
                        r"|inet6\s+(\S+)\s+prefixlen\s+(\d+)")
    flags = re.compile(r"^(.*) MTU:(\d+)\s+Metric:.*"
                       r"|^\S+:\s+flags=\d+<(\S+)>\s+mtu\s+(\d+)")
    newether = re.compile(r"^\s+ether\s+(\S+)")
    newifctype = re.compile(r"txqueuelen\s+\d+\s+\(([^)]+)\)")

    # variables for ip tool (ip addr)
    ip_chunk = re.compile(r"(^\d+:\s\S+:.*mtu.+?\n" "(\s+.+\n)*)",re.MULTILINE)
    ip_meta = re.compile(r"^(?P<ip_number>\d+):"               # Interface num +
                          "\s(?P<ip_name>\S+)"                 # Interface name +
                          ":\s+(?P<ip_flags>\S+)\s+"           # Flags +
                          "mtu\s+(?P<ip_mtu>\d+)\s+.+\n"       # MTU
                          "\s+link/(?P<ip_type>\S+)\s?"        # IF type +
                          "((?P<ip_mac>\S+).*)?\n"             # MAC
                          ".*",                                # Everything else
                           re.MULTILINE)
    ip4_addrs = re.compile(r"\s+inet\s(\S+).*\n", re.MULTILINE)
    ip6_addrs = re.compile(r"\s+inet6\s(\S+).*\n", re.MULTILINE)

    def process(self, device, results, log):
        log.info('Modeler %s processing data for device %s', self.name(), device.id)
        self.log = log
        ifconfig, dmesg, netspeed = results.split('__COMMAND__')
        if '###' in ifconfig:
            relMap = self.parseIpconfig(ifconfig, device, self.relMap())
        else:
            relMap = self.parseIfconfig(ifconfig, device, self.relMap())

        relMap = parseDmesg(dmesg.lstrip(), relMap)
        relMap = parseNetSpeed(netspeed.strip(), relMap)

        return relMap

    def parseIfconfig(self, ifconfig, device, relMap):
        """
        Parse the output of the ifconfig -a command.
        """
        rlines = ifconfig.splitlines()
        iface = None
        for line in rlines:

            # reset state to no interface
            if not line.strip():
                iface = None

            # new interface starting
            miface = self.ifstart.search(line)
            if miface:
                # start new interface and get name, type, and macaddress
                iface = self.objectMap()
                name = miface.group(1)

                iface.interfaceName = name
                iface.id = self.prepId(name)
                if self.isIgnoredName(device, iface.interfaceName):
                    continue

                relMap.append(iface)

            mtype = self.oldiftype.search(line)
            if mtype:
                if mtype.lastindex == 2:
                    itype, iface.macaddress = mtype.groups()[:2]
                else:
                    itype = mtype.group(3)

                if itype.startswith("Ethernet"):
                    itype = "ethernetCsmacd"
                iface.type = itype.strip()

                if self.isIgnoredType(device, iface.interfaceName, iface.type):
                    relMap.maps.remove(iface)
                    iface = None

                    continue

            # get the IP addresses of an interface
            maddr = self.v4addr.search(line)
            if maddr and iface:
                # get IP address and netmask
                if maddr.lastindex == 2:
                    ip, netmask = maddr.groups()[:2]
                else:
                    ip, netmask = maddr.groups()[2:]
                try:
                    netmask = self.maskToBits(netmask)
                except ValueError:
                    return relMap
                if not hasattr(iface, 'setIpAddresses'):
                    iface.setIpAddresses = []
                iface.setIpAddresses.append("%s/%s" % (ip, netmask))

            maddr = self.v6addr.search(line)
            if maddr and iface:
                # get IP address
                if maddr.lastindex == 3:
                    ip = "%s/%s" % maddr.groups()[1:]
                else:
                    ip = maddr.group(1)
                if not hasattr(iface, 'setIpAddresses'):
                    iface.setIpAddresses = []
                iface.setIpAddresses.append(ip)

            mether = self.newether.search(line)
            if mether and iface:
                # get MAC address (new style)
                macaddress = mether.group(1)
                iface.macaddress = macaddress

                iface.type = "ethernetCsmacd"

                if self.isIgnoredType(device, iface.interfaceName, iface.type):
                    relMap.maps.remove(iface)
                    iface = None

                continue

            mtype = self.newifctype.search(line)
            if mtype and iface:
                # get MAC address (new style)
                ifctype = mtype.group(1)

                iface.type = ifctype.strip()

                if self.isIgnoredType(device, iface.interfaceName, iface.type):
                    relMap.maps.remove(iface)
                    iface = None

                    continue

            # get the state UP/DOWN of the interface
            mstatus = self.flags.search(line)
            if mstatus and iface:
                # get adminStatus, operStatus, and mtu
                if mstatus.lastindex == 2:
                    flags, mtu = mstatus.groups()[:2]
                else:
                    flags, mtu = mstatus.groups()[2:]

                if "UP" in flags:
                    iface.operStatus = 1
                else:
                    iface.operStatus = 2

                if "RUNNING" in flags:
                    iface.adminStatus = 1
                else:
                    iface.adminStatus = 2
                iface.mtu = int(mtu)

        return relMap

    def parseIpconfig(self, ifconfig, device, relMap):
        """
        Parse the output of the ip addr command.
        """
        for match in self.ip_chunk.finditer(ifconfig):

            meta = self.ip_meta.match(match.group())
            if not meta:
                continue

            ip_name = meta.group('ip_name')
            dontCollectIntNames = getattr(device, 'zInterfaceMapIgnoreNames', None)
            if dontCollectIntNames and re.search(dontCollectIntNames, ip_name):
                self.log.debug(
                    "Interface %s matched the zInterfaceMapIgnoreNames zprop '%s'",
                    ip_name,
                    dontCollectIntNames)

                continue

            # Set the type adjustment
            itype = meta.group('ip_type')
            if itype.startswith("ether"):
                itype = "ethernetCsmacd"
            elif itype.startswith("loopback"):
                itype = "Local Loopback"
            ip_type = itype.strip()

            dontCollectIntTypes = getattr(device, 'zInterfaceMapIgnoreTypes', None)
            if dontCollectIntTypes and re.search(dontCollectIntTypes, ip_type):
                self.log.debug(
                    "Interface %s type %s matched the zInterfaceMapIgnoreTypes zprop '%s'",
                    ip_name,
                    ip_type,
                    dontCollectIntTypes)

                continue

            # create the iface and populate the base metadata
            iface = self.objectMap()
            iface.interfaceName = ip_name
            iface.type = ip_type
            iface.id = self.prepId(ip_name)
            iface.macaddress = meta.group('ip_mac')

            # Set flags data
            ip_flags = meta.group('ip_flags')
            if "UP" in ip_flags:
                iface.operStatus = 1
            else:
                iface.operStatus = 2

            if "LOWER_UP" in ip_flags:
                iface.adminStatus = 1
            else:
                iface.adminStatus = 2

            ip_mtu = meta.group('ip_mtu')
            if ip_mtu:
                iface.mtu = int(ip_mtu)

            # get the IP4 addresses of an interface
            ip4_addrs = self.ip4_addrs.findall(match.group())
            if ip4_addrs and not hasattr(iface, 'setIpAddresses'):
                iface.setIpAddresses = []

            for _ip in ip4_addrs:
                _ip = _ip.translate(None, '\(\)\', ')
                _ip = _ip.split("/")
                ip = _ip[0]
                try:
                    netmask = _ip[1]
                except IndexError:
                    # tun interfaces omit netmask because they're always /32
                    netmask = "32"
                iface.setIpAddresses.append("%s/%s" % (ip, netmask))

            # Get the IP6 addresses
            ip6_addrs = self.ip6_addrs.findall(match.group())
            if ip6_addrs and not hasattr(iface, 'setIpAddresses'):
                iface.setIpAddresses = []

            for ip in ip6_addrs:
                iface.setIpAddresses.append(ip)

            relMap.append(iface)

        return relMap

    def isIgnoredName(self, device, name):
        """Checks whether interface name in device's ignore list."""
        dontCollectIntNames = getattr(device, 'zInterfaceMapIgnoreNames', None)
        if dontCollectIntNames and re.search(dontCollectIntNames, name):
            self.log.debug("Interface %s matched the "
                           "zInterfaceMapIgnoreNames zprop '%s'", name,
                           dontCollectIntNames)
            return True

        return False

    def isIgnoredType(self, device, name, ifcType):
        """Checks whether interface type in device's ignore list."""
        dontCollectIntTypes = getattr(device, 'zInterfaceMapIgnoreTypes', None)
        if dontCollectIntTypes and re.search(dontCollectIntTypes, ifcType):
            self.log.debug("Interface %s type %s matched the "
                           "zInterfaceMapIgnoreTypes zprop '%s'", name,
                           ifcType, dontCollectIntTypes)
            return True

        return False
