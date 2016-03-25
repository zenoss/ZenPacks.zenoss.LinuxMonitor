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


    Properties:

        os.software: productKey, description, installDate


    Example command output:

    basesystem__FIELD__8.0__FIELD__5.1.1.el5.centos__FIELD__1224082539__FIELD__CentOS__FIELD__The skeleton package which defines a simple CentOS system.
    glibc__FIELD__2.5__FIELD__24__FIELD__1224082561__FIELD__CentOS__FIELD__The GNU libc libraries.
    libstdc++__FIELD__4.1.2__FIELD__42.el5__FIELD__1224082563__FIELD__CentOS__FIELD__GNU Standard C++ Library
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
QUERY_FORMAT = FIELD_DELIMETER.join(["%%{%s}" % field for field in FIELDS])


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


def parseResults(results):
    """
    Parse the results of the rpm command to create a dictionary of installed
    software.
    """
    softwareDicts = []
    for line in results.splitlines():
        fields = dict(zip(FIELDS, line.split(FIELD_DELIMETER)))
        if isCompleteLine(fields):
            softwareDicts.append(utils.createSoftwareDict(
                    "%(NAME)s %(VERSION)s-%(RELEASE)s" % fields,
                    fields["VENDOR"],
                    fields["SUMMARY"],
                    gmtime(int(fields["INSTALLTIME"]))))
    return softwareDicts


class rpm(SoftwareCommandPlugin):
    """
    Parse rpm -qa command output to get installed software.
    """

    command = r'`which rpm || echo true` -qa --qf "%s\n"' % QUERY_FORMAT

    def __init__(self):
        """
        Initialize this SoftwareCommandPlugin with the parseResults function
        from this module.
        """
        SoftwareCommandPlugin.__init__(self, parseResults)
