##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser


class vgsstatus(ComponentCommandParser):

    componentSplit = '\n'

    componentScanner = '(?P<component>\S+)'

    scanners = [
        r'\S+ *(?P<partial>\d+)'
        ]
