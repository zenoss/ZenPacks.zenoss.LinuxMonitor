##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2009, 2015-2016 all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


"""
A command parser.
    
 Command: 
        
    ifconfig -a
        
        
    Datapoints: 

        ifInPackets,  ifOutPackets,
        ifInErrors,   ifOutErrors,
        ifInOctets,   ifOutOctets,
        ifInDropped,  ifOutDropped,
        ifInOverruns, ifOutOverruns,
                      ifInFrame,
                      ifOutCarrier,
                      ifOutCollisions,
                      ifOutTxQueueLen


    Example command output:

        (old format)
        eth0      Link encap:Ethernet  HWaddr 00:0C:29:96:8A:0F
        ...
                  RX packets:15305 errors:0 dropped:0 overruns:0 frame:0
                  TX packets:12843 errors:0 dropped:0 overruns:0 carrier:0
                  collisions:0 txqueuelen:1000
                  RX bytes:2151990 (2.0 MiB)  TX bytes:1768340 (1.6 MiB)
        ...
        (new format)
        eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9001
        ...
                RX packets 1854  bytes 194008 (189.4 KiB)
                RX errors 0  dropped 0  overruns 0  frame 0
                TX packets 2225  bytes 542223 (529.5 KiB)
                TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        ...



    ip -o -s link

    Datapoints:

            ifInPackets,  ifOutPackets,
            ifInErrors,   ifOutErrors,
            ifInOctets,   ifOutOctets,
            ifInDropped,  ifOutDropped,
            ifInOverruns,
                          ifOutCarrier,
                          ifOutCollisions

    Example command output:

        1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT \    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\    RX: bytes  packets  errors  dropped overrun mcast   \    12410526612 1310601  0       0       0       0      \    TX: bytes  packets  errors  dropped carrier collsns \    12410526612 1310601  0       0       0       0
        2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9001 qdisc pfifo_fast state UP mode DEFAULT qlen 1000\    link/ether 0a:31:9f:21:b2:33 brd ff:ff:ff:ff:ff:ff\    RX: bytes  packets  errors  dropped overrun mcast   \    1589607358 1164071  0       0       0       0      \    TX: bytes  packets  errors  dropped carrier collsns \    48199848   622907   0       0       0       0

"""


from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser


RX = 'RX'
TX = 'TX'
IN = 'In'
OUT = 'Out'
BYTES = '\s+bytes(\s|:)(?P<if{0}Octets>\d+)'
PACKETS = '\s+packets(\s|:)(?P<if{0}Packets>\d+)'
ERRORS = '\s+errors(\s|:)(?P<if{0}Errors>\d+)'
DROPPED = '\s+dropped(\s|:)(?P<if{0}Dropped>\d+)'
OVERRUNS = '\s+overruns(\s|:)(?P<if{0}Overruns>\d+)'
FRAME = '\s+frame(\s|:)(?P<if{0}Frame>\d+)'
CARRIER = '\s+carrier(\s|:)(?P<if{0}Carrier>\d+)'
COLLISIONS = '\s+collisions(\s|:)(?P<if{0}Collisions>\d+)'
TXQUEUELEN = '\s+txqueuelen(\s|:)(?P<if{0}TxQueueLen>\d+)'


class DefaultScanConfig(object):
    # for ifconfig
    componentSplit = '\n\n'
    componentScanner = r'^(?P<component>\S+?):?[ \t]+'
    scanners = [
        # Debian, Ubuntu
        r''.join([RX, PACKETS, ERRORS, DROPPED, OVERRUNS, FRAME]).format(IN),
        r''.join([TX, PACKETS, ERRORS, DROPPED, OVERRUNS, CARRIER, COLLISIONS]).format(OUT),
        r''.join([RX, BYTES]).format(IN),
        r''.join([TX, BYTES]).format(OUT),
        # RedHat, CentOS
        r''.join([RX, PACKETS, BYTES]).format(IN),
        r''.join([RX, ERRORS, DROPPED, OVERRUNS, FRAME]).format(IN),
        r''.join([TX, PACKETS, BYTES]).format(OUT),
        r''.join([TX, ERRORS, DROPPED, OVERRUNS, CARRIER, COLLISIONS]).format(OUT),
        # Mixed
        r''.join([TXQUEUELEN]).format(OUT),
        ]
    componentScanValue = 'interfaceName'


class AltScanConfig(object):
    # for ip utility which produce very long output
    componentSplit = '\n'
    componentScanner = r'^(\d+):(\s)(?P<component>\S+?):?[ \t]+'
    scanners = [
        r'(.*)RX:(\s+)bytes(\s+)packets(\s+)errors(\s+)dropped(\s+)overrun(\s+)mcast(\s+)\\(\s+)(?P<ifInOctets>\d+)(\s+)(?P<ifInPackets>\d+)(\s+)(?P<ifInErrors>\d+)(\s+)(?P<ifInDropped>\d+)(\s+)(?P<ifInOverruns>\d+)',
        r'(.*)TX:(\s+)bytes(\s+)packets(\s+)errors(\s+)dropped(\s+)carrier(\s+)collsns(\s+)\\(\s+)(?P<ifOutOctets>\d+)(\s+)(?P<ifOutPackets>\d+)(\s+)(?P<ifOutErrors>\d+)(\s+)(?P<ifOutDropped>\d+)(\s+)(?P<ifOutCarrier>\d+)(\s+)(?P<ifOutCollisions>\d+)',
        ]
    componentScanValue = 'interfaceName'


class ifconfig(ComponentCommandParser):

    componentSplit = DefaultScanConfig.componentSplit
    componentScanner = DefaultScanConfig.componentScanner
    scanners = DefaultScanConfig.scanners
    componentScanValue = DefaultScanConfig.componentScanValue

    def processResults(self, cmd, result):
        # we try to use default parser values; if no result is produced
        # then try to use alternative regexp (for IP)
        super(ifconfig, self).processResults(cmd, result)
        if not result.values:
            self._setScanConfig(AltScanConfig)
            super(ifconfig, self).processResults(cmd, result)

    def _setScanConfig(self, config):
        self.componentSplit = config.componentSplit
        self.componentScanner = config.componentScanner
        self.scanners = config.scanners
        self.componentScanValue = config.componentScanValue
