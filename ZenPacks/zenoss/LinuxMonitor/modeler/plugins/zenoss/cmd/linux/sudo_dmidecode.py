##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2009, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


_doc__ = """sudo_dmidecode
Determine hardware information from the dmidecode command.
"""

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs


class sudo_dmidecode(CommandPlugin):
    """
    Sample output:

# dmidecode 2.7
SMBIOS 2.31 present.

Handle 0x0001, DMI type 1, 25 bytes.
System Information
        Manufacturer: VMware, Inc.
        Product Name: VMware Virtual Platform
        Version: None
        Serial Number: VMware-50 0a 32 b1 23 4f e8 1c-8f 19 26 3f df a6 93 7a
        UUID: 500A32B1-234F-E81C-8F19-263FDFA6937A
        Wake-up Type: Power Switch

    """
    
    maptype = "NewDeviceMap"
    command = 'sudo /usr/sbin/dmidecode -t 1'

    def process(self, device, results, log):
        """Collect command-line information from this device"""
        log.info("Processing the dmidecode -t 1 info for device %s",
                 device.id)
        if not results:
            log.warn("%s returned no results!", self.command)
            return

        log.debug("Results = %s", results.split('\n'))
        pairs = [ x.split(':',1) for x in results.split('\n') \
                       if x.startswith('\t') ]
        dmidecode = dict([ (x[0].strip(), x[1].strip()) for x in pairs ])

        om = self.objectMap()
        om.setHWProductKey = MultiArgs( dmidecode.get('Product Name', ''),
                                        dmidecode.get('Manufacturer', 'Unknown'))
        log.debug("HWProductKey=%s", om.setHWProductKey)
        om.setHWSerialNumber = dmidecode.get('Serial Number', '')
        log.debug("HWSerialNumber=%s", om.setHWSerialNumber)

        return om
