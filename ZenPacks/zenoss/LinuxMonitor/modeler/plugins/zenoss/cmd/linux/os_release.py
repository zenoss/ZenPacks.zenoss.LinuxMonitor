##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2016 all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


"""
Ubuntu output:

    DISTRIB_ID=Ubuntu
    DISTRIB_RELEASE=14.04
    DISTRIB_CODENAME=trusty
    DISTRIB_DESCRIPTION="Ubuntu 14.04.1 LTS"
    NAME="Ubuntu"
    VERSION="14.04.1 LTS, Trusty Tahr"
    ID=ubuntu
    ID_LIKE=debian
    PRETTY_NAME="Ubuntu 14.04.1 LTS"
    VERSION_ID="14.04"
    HOME_URL="http://www.ubuntu.com/"
    SUPPORT_URL="http://help.ubuntu.com/"
    BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"


Debian output:

    PRETTY_NAME="Debian GNU/Linux 7 (wheezy)"
    NAME="Debian GNU/Linux"
    VERSION_ID="7"
    VERSION="7 (wheezy)"
    ID=debian
    ANSI_COLOR="1;31"
    HOME_URL="http://www.debian.org/"
    SUPPORT_URL="http://www.debian.org/support/"
    BUG_REPORT_URL="http://bugs.debian.org/"


RedHat output:

    NAME="Red Hat Enterprise Linux Server"
    VERSION="7.2 (Maipo)"
    ID="rhel"
    ID_LIKE="fedora"
    VERSION_ID="7.2"
    PRETTY_NAME="Red Hat Enterprise Linux Server 7.2 (Maipo)"
    ANSI_COLOR="0;31"
    CPE_NAME="cpe:/o:redhat:enterprise_linux:7.2:GA:server"
    HOME_URL="https://www.redhat.com/"
    BUG_REPORT_URL="https://bugzilla.redhat.com/"

    REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
    REDHAT_BUGZILLA_PRODUCT_VERSION=7.2
    REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
    REDHAT_SUPPORT_PRODUCT_VERSION="7.2"
    Red Hat Enterprise Linux Server release 7.2 (Maipo)
    Red Hat Enterprise Linux Server release 7.2 (Maipo)


CentOS output:

    CentOS Linux release 7.1.1503 (Core)
    NAME="CentOS Linux"
    VERSION="7 (Core)"
    ID="centos"
    ID_LIKE="rhel fedora"
    VERSION_ID="7"
    PRETTY_NAME="CentOS Linux 7 (Core)"
    ANSI_COLOR="0;31"
    CPE_NAME="cpe:/o:centos:centos:7"
    HOME_URL="https://www.centos.org/"
    BUG_REPORT_URL="https://bugs.centos.org/"

    CENTOS_MANTISBT_PROJECT="CentOS-7"
    CENTOS_MANTISBT_PROJECT_VERSION="7"
    REDHAT_SUPPORT_PRODUCT="centos"
    REDHAT_SUPPORT_PRODUCT_VERSION="7"

    CentOS Linux release 7.1.1503 (Core)
    CentOS Linux release 7.1.1503 (Core)

"""


__doc__ = """os_release
Collect linux release information using the `cat /etc/*-release` command.
"""


import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin


SUPPORTED_DISTROS = (
    'ubuntu',
    'debian',
    'redhat',
    'centos',
    'suse',
)


RE_DISTR = re.compile('(\w+(\s|/)){1,}(\d+(\.)?){1,}\s[A-Za-z()]+')


def getOSModel(results):
    for line in results.split('\n'):
        fline = ''.join(line.split()).lower()
        if fline and any((d in fline for d in SUPPORTED_DISTROS)):
            if 'pretty_name' in fline:
                return line.split('=')[1].strip('"')
            elif RE_DISTR.match(line):
                return line.strip()


class os_release(LinuxCommandPlugin):

    maptype = 'DeviceMap'
    command = '/bin/cat /etc/*-release'
    compname = ''

    def process(self, device, results, log):
        log.info("Processing the cat /etc/*-release info for device %s" % device.id)
        osModel = getOSModel(results) or "Unknown Linux"

        om = self.objectMap()
        om.setOSProductKey = osModel

        return om
