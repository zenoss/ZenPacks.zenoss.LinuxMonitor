##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

import logging
log = logging.getLogger("zen.migrate")


class INodeUtilizationGraph(ZenPackMigration):

    version = Version(2, 0, 0)

    def migrate(self, pack):
        log.info('Fixing the Linux FileSystem template')
        try:
            path = '/zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/FileSystem'
            template = pack.dmd.unrestrictedTraverse(path)
        except Exception:
            log.debug('Unable to find FileSystem template')
        else:
            graph = template.graphDefs._getOb('Inode Utilization')
            graph.custom = ''
            for gp in graph.graphPoints():
                if gp.id in ['totalInodes', 'usedInodes']:
                    graph.graphPoints._delObject(gp.id)
                    log.info(
                        "Removing '{0}' graphpoint from {1} graph".format(
                            gp.id, graph.id
                        )
                    )

INodeUtilizationGraph()
