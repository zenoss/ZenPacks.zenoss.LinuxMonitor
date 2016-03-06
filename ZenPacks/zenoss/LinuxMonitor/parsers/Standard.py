##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""General-purpose parser.

Uses the command run to parse output appropriately. This is done to avoid
littering the COMMAND datasource parser selection with lots of single-purpose
non-reusable parsers.

Currently the following commands are supported.

* true

"""

from Products.ZenRRD.CommandParser import CommandParser
from zenoss.protocols.protobufs.zep_pb2 import SEVERITY_ERROR


def echo_test(datasource, results):
    """Handle result of "/usr/bin/env echo TEST".

    No handling is done. This datasource only exists as an "SSH ping" happening
    every 60 seconds. Any resulting SSH connectivity event will be raised and
    cleared by zencommand.

    """
    pass


def no_handler(datasource, results):
    """Handle datasources for which we have no handler.

    These would be configuration or coding issues. Not something that would
    represent a problem with monitored resources.

    """
    summary = (
        "{} datasource not supported by parser"
        ).format(datasource.name)

    results.events.append({
        "summary": summary,
        "device": datasource.deviceConfig.id,
        "component": datasource.component,
        "eventClass": "/App/Zenoss",
        "severity": SEVERITY_ERROR,
        "parser": __name__,
        })


# Keys in HANDLERS must match a COMMAND datasource's commandTemplate property
# exactly. It is a case-sensitive match.
HANDLERS = {
    "/usr/bin/env echo TEST": echo_test,
    }


class Standard(CommandParser):

    createDefaultEventUsingExitCode = False

    def processResults(self, datasource, results):
        HANDLERS.get(datasource.command, no_handler)(datasource, results)
