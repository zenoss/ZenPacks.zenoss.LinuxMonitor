##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2016-2017 all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


__doc__ = """os_release
Collect linux release information using the `cat /etc/*-release` command.
"""


import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs


SUPPORTED_DISTROS =  {'debian':'Debian', 'ubuntu':'Ubuntu','centos':'CentOS','redhat': 'RedHat', 'suse': 'Novell', 'red hat': 'RedHat'}


RE_DISTR = re.compile('(?P<os>(\w+(\s|\/)){1,}(\d+(\.)?){1,}\s[A-Za-z()]+)')


def combineNameAndVersion(results):
    """Combine the OS Model name and version using the results.

    Args:
        results (list): Entries from *-release files to parse.

    Returns:
        list: Updated entries from the *-release files to parse.

    """
    lines = results.split('\n')
    namePrefix = 'NAME='
    versionPrefix = 'VERSION='
    if namePrefix in results and versionPrefix in results:
        nameAndVersion = ''
        newLines = []
        for line in lines:
            if line.startswith(namePrefix):
                name = line.replace(namePrefix, '').strip('"')
                if name:
                    nameAndVersion = name
            elif nameAndVersion and line.startswith(versionPrefix):
                version = line.replace(versionPrefix, '').strip('"')
                if version:
                    nameAndVersion = nameAndVersion + ' ' + version
            elif line:
                newLines.append(line)
        if nameAndVersion:
            nameAndVersion = 'NAME_AND_VERSION=' + nameAndVersion
            newLines.insert(0, nameAndVersion)
        lines = newLines
    return lines


def getOSModel(results):
    """Get the OS Model name and version from the results.

    Args:
        results (list): Entries from the *-release files to parse.

    Returns:
        str: The OS Model name and version.

    """
    highPriorityFields = ('pretty_name', 'distrib_description')
    lines = combineNameAndVersion(results)
    for line in lines:
        fline = ''.join(line.split()).lower()
        if fline and any((distro in fline for distro in SUPPORTED_DISTROS.keys())):
            if any([hpField in fline for hpField in highPriorityFields]):
                return line.split('=')[1].strip('"')
            match = RE_DISTR.search(line)
            if match:
                return match.group('os').strip()


class os_release(LinuxCommandPlugin):

    maptype = 'DeviceMap'
    command = '/bin/cat /etc/*-release'
    compname = ''

    def process(self, device, results, log):
        """Determine the OS Model name and version from the results.

        Args:
            device (DeviceProxy): The modeled device proxy instance.
            results (list): Entries from the *-release files to parse.
            log (logging.Logger): ZenModeler Logger instance.

        Returns:
            ObjectMap: An object with the defined OS Model.

        """
        log.info(
            "Processing the cat /etc/*-release info for device %s",
            device.id)

        osModel = getOSModel(results) or "Unknown Linux"
        osManufacturer = None
        for distro in SUPPORTED_DISTROS.keys():
            if distro in osModel.lower():
                osManufacturer = SUPPORTED_DISTROS[distro]
        om = self.objectMap()
        om.setOSProductKey = MultiArgs(osModel, osManufacturer)

        return om
