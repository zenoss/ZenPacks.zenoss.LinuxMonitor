##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


import logging
import re

from Products.DataCollector.DeviceProxy import DeviceProxy
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.LinuxMonitor.modeler.plugins.zenoss.cmd.linux.os_release \
    import os_release
from Products.DataCollector.plugins.DataMaps import MultiArgs


LOG = logging.getLogger("zen.testcases")


class TestOSReleasePlugin(BaseTestCase):

    def afterSetUp(self):
        self.device = DeviceProxy()
        self.device.id = "test-device"
        self.plugin = os_release()

    def testRedHatInput(self):
        input = """
            NAME="Red Hat Enterprise Linux Server"
            VERSION="7.2 (Maipo)"
            ID="rhel"
            ID_LIKE="fedora"
            VERSION_ID="7.2"
            PRETTY_NAME="Red Hat Enterprise Linux Server"
            ANSI_COLOR="0;31"
            CPE_NAME="cpe:/o:redhat:enterprise_linux:7.2:GA:server"
            HOME_URL="https://www.redhat.com/"
            BUG_REPORT_URL="https://bugzilla.redhat.com/"

            REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
            REDHAT_BUGZILLA_PRODUCT_VERSION=7.2
            REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
            REDHAT_SUPPORT_PRODUCT_VERSION="7.2"
            Red Hat Enterprise Linux Server release 7.2(Maipo)
            Red Hat Enterprise Linux Server release 7.2(Maipo)
        """
        input = re.sub('\s{2,}', '\n', input.strip())
        om = self.plugin.process(self.device, input, LOG)
        self.assertEquals(
            str(om.setOSProductKey), str(MultiArgs("Red Hat Enterprise Linux Server 7.2 (Maipo)", "RedHat")))

    def testCentOSInput(self):
        input = """
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
        input = re.sub('\s{2,}', '\n', input.strip())
        om = self.plugin.process(self.device, input, LOG)
        self.assertEquals(
            str(om.setOSProductKey), str(MultiArgs("CentOS Linux 7 (Core)", "CentOS")))

    def testDebianInput(self):
        input = """
            PRETTY_NAME="Debian GNU/Linux 7 (wheezy)"
            NAME="Debian GNU/Linux"
            VERSION_ID="7"
            VERSION="7 (wheezy)"
            ID=debian
            ANSI_COLOR="1;31"
            HOME_URL="http://www.debian.org/"
            SUPPORT_URL="http://www.debian.org/support/"
            BUG_REPORT_URL="http://bugs.debian.org/"
        """
        input = re.sub('\s{2,}', '\n', input.strip())
        om = self.plugin.process(self.device, input, LOG)
        self.assertEquals(
            str(om.setOSProductKey), str(MultiArgs("Debian GNU/Linux 7 (wheezy)","Debian")))

    def testUbuntuInput(self):
        input = """
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
        """
        input = re.sub('\s{2,}', '\n', input.strip())
        om = self.plugin.process(self.device, input, LOG)
        self.assertEquals(
            str(om.setOSProductKey), str(MultiArgs("Ubuntu 14.04.1 LTS","Ubuntu")))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOSReleasePlugin))
    return suite
