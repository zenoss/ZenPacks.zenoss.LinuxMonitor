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


class DevCpuUtilizationGraph(ZenPackMigration):

    version = Version(2, 0, 0)

    def migrate(self, pack):
        log.info('Fixing the Device template')
        try:
            path = '/zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/Device'
            template = pack.dmd.unrestrictedTraverse(path)
            graph = template.graphDefs._getOb('CPU Utilization')
        except Exception:
            log.debug('Unable to find CPU Utilization graph for Device')
        else:
            template.graphDefs._delObject(graph.id)
            log.info("Removing redundant {0} graph".format(graph.id))

DevCpuUtilizationGraph()
