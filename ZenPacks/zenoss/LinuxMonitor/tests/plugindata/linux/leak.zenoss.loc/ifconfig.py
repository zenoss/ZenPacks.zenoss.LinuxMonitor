##########################################################################
#
#   Copyright 2009 Zenoss, Inc. All Rights Reserved.
#
##########################################################################
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
