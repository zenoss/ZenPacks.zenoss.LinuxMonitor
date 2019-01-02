##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging

from pprint import pformat

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.CommandParser import ParsedResults

from ..parsers.linux.iostats import iostats

# Disable logging to stdout (or anywhere else)
rootLogger = logging.getLogger()
rootLogger.handlers = []
handler = logging.NullHandler()
rootLogger.addHandler(handler)


class Object(object):

    def __init__(self, **kw):
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return pformat(dict(
            (attr, getattr(self, attr))
            for attr in dir(self)
            if not attr.startswith('__')
        ))


def _getDatapoint(data, name):
    """
    """
    return next(
        ((dp, v) for dp, v in data if dp["id"] == name),
        (None, None)
    )


class TestIostatsParser(BaseTestCase):
    """
    
    """

    def setUp(self):
        self.cmd = Object(**{
            "deviceConfig": Object(**{
                "device": "localhost",
                "lastmodeltime": "lastmodeltime"
            }),
            "command": "command",
            "component": "",
            "points": [
                Object(**{
                    "id": "bandwidthUtilCurrent"
                }),
                Object(**{
                    "id": "bandwidthUtilAvg"
                })
            ]
        })
        self.cmd.result = Object(**{"exitCode": 0})

    def tearDown(self):
        self.cmd = None
        del self.cmd

    def test_DataPointsParsedComponent1(self):
        """

        :return:
        """
        self.cmd.result.output = """
        Linux 3.2.0-29-generic (qa-ubuntu-12)   12/31/2018      _x86_64_        (2 CPU)
        Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
        sda               0.00     0.19    0.84    0.31     0.00     0.00    10.89     0.00    1.23    0.99    1.90   0.60   0.07
        sda1              0.00     0.00    0.07    0.00     0.00     0.00     4.05     0.00    3.69    3.69    4.31   3.04   0.02
        
        Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
        sda               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
        sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
        """

        results = ParsedResults()
        self.cmd.component = "disk-sda1"
        iostats().processResults(self.cmd, results)
        self.assertEqual(len(results.values), 2)
        utilCurrent, utilCurrentValue = _getDatapoint(results.values, "bandwidthUtilCurrent")
        utilAvg, utilAvgValue = _getDatapoint(results.values, "bandwidthUtilAvg")

        self.assertEqual(utilCurrentValue, 0.02)
        self.assertEqual(utilAvgValue, 0.0)

    def test_DataPointsParsedComponent2(self):
        """

        :return:
        """
        self.cmd.result.output = """
            Linux 3.2.0-29-generic (qa-ubuntu-12)   12/31/2018      _x86_64_        (2 CPU)
            Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
            sda               0.00     0.19    0.84    0.31     0.00     0.00    10.89     0.00    1.23    0.99    1.90   0.60   0.07
            sda1              0.00     0.00    0.07    0.00     0.00     0.00     4.05     0.00    3.69    3.69    4.31   3.04   0.02

            Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
            sda               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
            sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
            """

        results = ParsedResults()
        self.cmd.component = "disk-sda"
        iostats().processResults(self.cmd, results)
        self.assertEqual(len(results.values), 2)
        utilCurrent, utilCurrentValue = _getDatapoint(results.values, "bandwidthUtilCurrent")
        utilAvg, utilAvgValue = _getDatapoint(results.values, "bandwidthUtilAvg")

        self.assertEqual(utilCurrentValue, 0.07)
        self.assertEqual(utilAvgValue, 0.0)

    def test_WrongComponentName(self):
        """

        :return:
        """
        self.cmd.result.output = """
            Linux 3.2.0-29-generic (qa-ubuntu-12)   12/31/2018      _x86_64_        (2 CPU)
            Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
            sda               0.00     0.19    0.84    0.31     0.00     0.00    10.89     0.00    1.23    0.99    1.90   0.60   0.07
            sda1              0.00     0.00    0.07    0.00     0.00     0.00     4.05     0.00    3.69    3.69    4.31   3.04   0.02

            Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
            sda               0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
            sda1              0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
            """

        results = ParsedResults()
        self.cmd.component = "disk-sda2"
        iostats().processResults(self.cmd, results)
        self.assertEqual(len(results.values), 0)

    def test_EmptyCommandOutput(self):
        """

        :return:
        """
        self.cmd.result.output = ""

        results = ParsedResults()
        self.cmd.component = "disk-sda2"
        iostats().processResults(self.cmd, results)
        self.assertEqual(len(results.values), 0)
