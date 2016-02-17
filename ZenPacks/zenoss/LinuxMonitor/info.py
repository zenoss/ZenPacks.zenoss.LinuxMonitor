##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.Zuul.infos.component.filesystem import FileSystemInfo as BaseFileSystemInfo
from Products.Zuul.decorators import info


class FileSystemInfo(BaseFileSystemInfo):

    @property
    @info
    def logicalvolume(self):
        return self._object.getLogicalVolume()
