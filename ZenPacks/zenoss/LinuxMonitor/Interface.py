##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import schema
from Products.ZenModel.IpInterface import IpInterface


class Interface(schema.Interface):
    '''
    Model class for Interface
    '''
    portal_type = meta_type = 'IpInterface'

    def monitored(self):
        """
        Override default method to monitor status of Interface component
        even if adminStatus is not RUNNING, because it can be changed during monitoring
        """
        return super(IpInterface, self).monitored()

    def snmpIgnore(self):
        """Override default method to use getAdminStatus method instead of adminStatus property directly."""
        # This must be based off the modeled admin status or zenhub could
        # lock itself up while building configurations.
        return self.getAdminStatus() > 1 or self.monitor is False

    def getAdminStatus(self):
        """Override default method to get AdminStatus based on monitoring data."""
        dp_data = self.datapointAdminStatus()
        if dp_data:
            return int(dp_data)

        return self.adminStatus

    def getOperStatus(self):
        """Override default method to get OperStatus based on monitoring data."""
        dp_data = self.datapointOperStatus()
        if dp_data:
            return int(dp_data)
        return self.operStatus
