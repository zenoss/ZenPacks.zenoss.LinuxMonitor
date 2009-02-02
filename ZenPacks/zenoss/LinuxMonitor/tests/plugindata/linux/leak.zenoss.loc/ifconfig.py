###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
{
"ifconfig":
    {
    "eth0": dict(
        adminStatus=1,
        macaddress="00:50:56:8A:29:37",
        mtu=1500,
        operStatus=1,
        setIpAddresses=["10.175.211.115/24"],
        type="ethernetCsmacd"),

    "lo": dict(
        adminStatus=1,
        mtu=16436,
        operStatus=1,
        setIpAddresses=["127.0.0.1/8"],
        type="Local Loopback"),
    
    "sit0": dict(
        adminStatus=2,
        classname="",
        compname="os",
        mtu=1480,
        operStatus=2,
        type="IPv6-in-IPv4")
    }
}
