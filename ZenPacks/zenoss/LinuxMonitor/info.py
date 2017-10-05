##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from zope.interface import implements
from Products.Zuul.infos.component.ipinterface import IpInterfaceInfo

from ZenPacks.zenoss.LinuxMonitor.interfaces import IInterfaceInfo


class InterfaceInfo(IpInterfaceInfo):
    implements(IInterfaceInfo)
