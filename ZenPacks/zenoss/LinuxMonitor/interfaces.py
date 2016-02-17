##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IFileSystemInfo as LIFileSystemInfo

from Products.Zuul.utils import ZuulMessageFactory as _t


class IFileSystemInfo(LIFileSystemInfo):
    logicalvolume = schema.Entity(title=_t(u"Logical Volume"), readonly=True, group="Details")
