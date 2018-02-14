##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2009, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


_doc__ = """alt_kernel_name
Determine kernel information from the /etc/issue file. 
"""

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.ZenUtils.Utils import prepId


class alt_kernel_name(CommandPlugin):
    """
    Sample output:

CentOS release 5.2 (Final)
Kernel \r on an \m

    """
    
    maptype = "NewDeviceMap"
    command = '/bin/cat /etc/issue'

    def process(self, device, results, log):
        """Collect command-line information from this device"""
        log.info("Processing the kernel info for device %s",
                 device.id)
        if not results:
            log.warn("%s returned no results!", self.command)
            return

        log.debug("Results = %s", results.split('\n'))
        fixed_res = ""
        for line in results.split('\n'):
                if not line.startswith("#"):
                        fixed_res += line
        results = fixed_res
        om = self.objectMap()
        # Make sure OSProductKey is a valid id
        om.setOSProductKey = prepId(results)
        log.debug("setOSProductKey = %s", om.setOSProductKey)

        return om
