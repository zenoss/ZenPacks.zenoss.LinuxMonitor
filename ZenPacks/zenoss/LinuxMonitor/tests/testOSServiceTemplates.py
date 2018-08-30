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
from ZenPacks.zenoss.LinuxMonitor import OS_SERVICE_MODELER_VERSION
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

        # Service modeled by "too old" of a modeler plugin (ZPS-4334).
        service.modeler_version = None
        service.init_system = 'SYSTEMD'
        self.assertEqual(len(service.getRRDTemplates()), 0)
        service.modeler_version = 0
        self.assertEqual(len(service.getRRDTemplates()), 0)

        # Set current modeler_version for remaining tests.
        service.modeler_version = OS_SERVICE_MODELER_VERSION

        # No init system modeled.
        service.init_system = None
        self.assertEqual(len(service.getRRDTemplates()), 0)

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
