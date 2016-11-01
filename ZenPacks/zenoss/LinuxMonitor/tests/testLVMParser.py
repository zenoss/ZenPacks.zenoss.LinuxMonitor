#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    Test Linux attribute parser for ZEN-25792 fix
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.LinuxMonitor.util import LVMAttributeParser

unused(Globals)

EL6_VG = 'wz--n-'
EL6_VG_EXPECTED = ['writeable', 'resizable', 'normal']

RHEL63_LV = '-wi-ao--'
RHEL68_LV = '-wi-ao--p-'
RHEL63_LV_EXPECTED = ['writeable', 'inherited', 'active', 'open']
RHEL68_LV_EXPECTED = ['writeable', 'inherited', 'active', 'open', 'partial']

SKIP_ACTIVATION = '-wi-ao--pk'
SKIP_ACTIVATION_EXPECTED = ['writeable', 'inherited', 'active', 'open', 'partial', 'skip activation']

UBUNTU_LV = 'twi-i-tz-'
UBUNTU_LV_EXPECTED = ['thin pool', 'writeable', 'inherited', 'mapped device present with inactive table', 'thin']

PV = 'axm'
PV_EXPECTED = ['allocatable', 'exported', 'missing']

VG_PERMISSIONS = {'w': 'writeable',
                  'r': 'read-only',
                  '-': None}
VG_ALLOCATION_POLICY = {'c': 'contiguous',
                        'l': 'cling',
                        'n': 'normal',
                        'a': 'anywhere'}
VG_CLUSTER = {'c': 'clustered',
              's': 'shared'}
LV_VOLUME_TYPE = {'m': 'mirrored',
                  'M': 'mirrored without initial sync',
                  'o': 'origin',
                  'O': 'origin with merging snapshot',
                  'r': 'raid',
                  'R': 'raid without initial sync',
                  's': 'snapshot',
                  'S': 'merging snapshot',
                  'p': 'pvmove',
                  'v': 'virtual',
                  'i': 'mirror or raid image',
                  'I': 'image out of sync',
                  'l': 'mirror log device',
                  'c': 'under conversion',
                  'V': 'thin volume',
                  't': 'thin pool',
                  'T': 'thin pool data',
                  'e': 'raid or thin pool metadata'}
LV_PERMISSIONS = {'w': 'writeable',
                  'r': 'read-only',
                  'R': 'read-only activation of non-read-only volume'}
LV_ALLOCATION_POLICY = {'a': 'anywhere',
                        'c': 'contiguous',
                        'i': 'inherited',
                        'l': 'cling',
                        'n': 'normal',
                        'A': 'anywhere (Locked)',
                        'C': 'contiguous (Locked)',
                        'I': 'inherited (Locked)',
                        'L': 'cling (Locked)',
                        'N': 'normal (Locked)'}
LV_STATE = {'a': 'active',
            's': 'suspended',
            'I': 'invalid snapshot',
            'S': 'invalid suspended snapshot',
            'm': 'snapshot merge failed',
            'M': 'suspended snapshot merge failed',
            'd': 'mapped device present without tables',
            'i': 'mapped device present with inactive table'}
LV_DEVICE = {'o': 'open',
             'X': 'unknown'}
LV_TARGET_TYPE = {'C': 'cache',
                  'm': 'mirror',
                  'r': 'raid',
                  's': 'snapshot',
                  't': 'thin',
                  'u': 'unknown',
                  'v': 'virtual'}
LV_HEALTH = {'p': 'partial',
             'r': 'refresh needed',
             'm': 'mismatches exist',
             'w': 'writemostly',
             'X': 'unknown'}


class TestLVMAttributeParser(BaseTestCase):
    """Test Event Classes
    """

    def test_att_parser(self):
        parser = LVMAttributeParser()
        attributes = parser.pv_attributes(PV)
        self.assertEquals(attributes, PV_EXPECTED)
        attributes = parser.vg_attributes(EL6_VG)
        self.assertEquals(attributes, EL6_VG_EXPECTED)
        attributes = parser.lv_attributes(RHEL63_LV)
        self.assertEquals(attributes, RHEL63_LV_EXPECTED)
        attributes = parser.lv_attributes(RHEL68_LV)
        self.assertEquals(attributes, RHEL68_LV_EXPECTED)
        attributes = parser.lv_attributes(UBUNTU_LV)
        self.assertEquals(attributes, UBUNTU_LV_EXPECTED)
        attributes = parser.lv_attributes(SKIP_ACTIVATION)
        self.assertEquals(attributes, SKIP_ACTIVATION_EXPECTED)

        for k, v in VG_PERMISSIONS.items():
            self.assertEquals(parser.vg_permissions(k), v)
        for k, v in VG_ALLOCATION_POLICY.items():
            self.assertEquals(parser.vg_allocation_policy(k), v)
        for k, v in VG_CLUSTER.items():
            self.assertEquals(parser.vg_cluster(k), v)

        for k, v in LV_VOLUME_TYPE.items():
            self.assertEquals(parser.lv_volume_type(k), v)
        for k, v in LV_PERMISSIONS.items():
            self.assertEquals(parser.lv_permissions(k), v)
        for k, v in LV_ALLOCATION_POLICY.items():
            self.assertEquals(parser.lv_allocation_policy(k), v)
        for k, v in LV_STATE.items():
            self.assertEquals(parser.lv_state(k), v)
        for k, v in LV_DEVICE.items():
            self.assertEquals(parser.lv_device(k), v)
        for k, v in LV_TARGET_TYPE.items():
            self.assertEquals(parser.lv_target_type(k), v)
        for k, v in LV_HEALTH.items():
            self.assertEquals(parser.lv_health(k), v)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLVMAttributeParser))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
