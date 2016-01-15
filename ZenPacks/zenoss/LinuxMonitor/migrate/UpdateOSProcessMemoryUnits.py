##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

import logging
log = logging.getLogger("zen.migrate")


class UpdateOSProcessMemoryUnits(ZenPackMigration):

    # On GNU\Linux systems, ps utility reports RSS metric in kiloBytes.
    # Currently OSProcess graphs for /Devices/Server/SSH/Linux are rendered with "bytes" units,
    # so purpose of this migrate script is to have propper units on graphs.

    version = Version(2, 0, 0)

    def migrate(self, pack):
        try:
            path = '/zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/OSProcess'
            template = pack.dmd.unrestrictedTraverse(path)
        except Exception:
            log.debug('Unable to find OSProcess template')
        else:
            graph = template.graphDefs._getOb('Memory')
            if graph.units == 'bytes' and not graph.graphPoints.mem.rpn:
                graph.graphPoints.mem.rpn = "1024,*"
                log.info('Fixing RPN on OSProcess template')

UpdateOSProcessMemoryUnits()
