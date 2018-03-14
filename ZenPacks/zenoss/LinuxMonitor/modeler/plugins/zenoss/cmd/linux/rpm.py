##############################################################################
#
# Copyright (C) Zenoss, Inc. 2009, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""rpm
Modeler plugin

    Commands:

        "rpm -qa --qf <query format>"
        "dpkg-query -W -f = <query format>"

    Properties:

        os.software: productKey, description, installDate


    Example command output:

    basesystem__FIELD__8.0__FIELD__5.1.1.el5.centos__FIELD__1224082539__FIELD__CentOS__FIELD__The skeleton package which defines a simple CentOS system.
    glibc__FIELD__2.5__FIELD__24__FIELD__1224082561__FIELD__CentOS__FIELD__The GNU libc libraries.
    libstdc++__FIELD__4.1.2__FIELD__42.el5__FIELD__1224082563__FIELD__CentOS__FIELD__GNU Standard C++ Library
    _field:accountsservice_field:1470949489
    _field:acpid_field:1456156128
    _field:accountsservice_field:0.6.37-1ubuntu10.1_field:Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>_field:query and manipulate user account information
     The AccountService project provides a set of D-Bus
     interfaces for querying and manipulating user account
     information and an implementation of these interfaces,
     based on the useradd, usermod and userdel commands.
    _field:acpid_field:1:2.0.23-1ubuntu1_field:Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>_field:Advanced Configuration and Power Interface event daemon
     Modern computers support the Advanced Configuration and Power Interface (ACPI)
     to allow intelligent power management on your system and to query battery and
     configuration status.
 .
    ...

"""

import logging
from time import gmtime

import Products.DataCollector.CommandPluginUtils as utils

from Products.DataCollector.plugins.CollectorPlugin \
        import SoftwareCommandPlugin


log = logging.getLogger("zen.rpm")
FIELD_DELIMETER = "__FIELD__"
FIELDS = ["NAME", "VERSION", "RELEASE", "INSTALLTIME", "VENDOR", "SUMMARY"]
VENDOR_DICT = {'debian':'Debian', 'ubuntu':'Ubuntu','centos':'CentOS','redhat': 'RedHat'}

def isCompleteLine(fields):
    """
    Does the dictionary that is passed in have all the keys listed in FIELDS.
    """
    for key in FIELDS:
        if key not in fields:
            retval = False
            break
    else:
        retval = True
    return retval

def getVendor(maintainer):
    for vendor in VENDOR_DICT.keys():
        if vendor in maintainer.lower():
            return VENDOR_DICT[vendor]
    return maintainer.split(' <')[0]

def parseDpkgResults(results, softwareDicts):
    """
    Parse the results of the dpkg command to create a dictionary of installed
    software.
    """
    timeDict = {}
    for line in results.splitlines():
        line = line.split('_field:')[1:]
        if len(line) == 2:
            timeDict[line[0].rsplit(':',1)[0]] = gmtime(int(line[1]))
        elif line and '' not in line and line[0] in timeDict:
            softwareDicts.append(utils.createSoftwareDict(
                    line[0] + ' ' + line[1],
                    getVendor(line[2]),
                    line[3],
                    timeDict[line[0]]))
    return softwareDicts

def parseRpmResults(results, softwareDicts):
    """
    Parse the results of the rpm command to create a dictionary of installed
    software.
    """
    for line in results.splitlines():
        fields = dict(zip(FIELDS, line.split(FIELD_DELIMETER)))
        if isCompleteLine(fields):
            softwareDicts.append(utils.createSoftwareDict(
                    "%(NAME)s %(VERSION)s-%(RELEASE)s" % fields,
                    fields["VENDOR"],
                    fields["SUMMARY"],
                    gmtime(int(fields["INSTALLTIME"]))))
    return softwareDicts

def parseResults(results):
    softwareDicts = []
    rpmResults, dpkgResults = results.split('_SPLIT_',1)
    softwareDicts = parseRpmResults(rpmResults, softwareDicts)
    softwareDicts = parseDpkgResults(dpkgResults, softwareDicts)
    return softwareDicts

class rpm(SoftwareCommandPlugin):
    """
    Parse rpm -qa and dpkg-query command output to get installed software.
    """

    command = ( 'export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin; '
                '$(which rpm || echo true) -qa --qf "%{NAME}__FIELD__%{VERSION}__FIELD__%{RELEASE}__FIELD__%{INSTALLTIME}__FIELD__%{VENDOR}__FIELD__%{SUMMARY}\\n"; '
                'echo "_SPLIT_"; '
                'if command -v dpkg >/dev/null 2>&1; then '
                'for file_list in $(ls /var/lib/dpkg/info/*.list); '
                'do stat_result=$(stat --format=%Y "$file_list"); '
                'printf "_field:%s_field:%s\\n" "$(basename $file_list .list)" "$stat_result"; '
                'done; '
                '''dpkg-query -W -f='_field:${Package}_field:${Version}_field:${Maintainer}_field:${Description}\\n'; '''
                'fi'
                )
    def __init__(self):
        """
        Initialize this SoftwareCommandPlugin with the parseResults function
        from this module.
        """
        SoftwareCommandPlugin.__init__(self, parseResults)
