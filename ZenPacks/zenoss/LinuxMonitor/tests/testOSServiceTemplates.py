##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging
import unittest

from Products.ZenModel.RRDTemplate import manage_addRRDTemplate
from ZenPacks.zenoss.LinuxMonitor.LinuxService import LinuxService

LOG = logging.getLogger("zen.testcases")


class ServiceTemplateTests(unittest.TestCase):
    def test_serviceTemplates(self):
        service = LinuxService("test_service")

        # Add few templates to LinuxService component
        manage_addRRDTemplate(service, "OSService-UPSTART")
        manage_addRRDTemplate(service, "OSService-SYSTEMV")
        manage_addRRDTemplate(service, "OSService-SYSTEMD")
        manage_addRRDTemplate(service, "Extra-Template")
        manage_addRRDTemplate(service, "Another-Extra-Template")

        # SYSTEMD tests
        service.init_system = 'SYSTEMD'
        templates = service.getRRDTemplates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, 'OSService-SYSTEMD')

        # UPSTART tests
        service.init_system = 'UPSTART'
        templates = service.getRRDTemplates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, 'OSService-UPSTART')

        # SYSTEMV tests
        service.init_system = 'SYSTEMV'
        templates = service.getRRDTemplates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, 'OSService-SYSTEMV')

        # OTHER-INIT tests
        service.init_system = 'OTHER-INIT'
        templates = service.getRRDTemplates()
        self.assertEqual(len(templates), 0)
