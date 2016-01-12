##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import Globals
import transaction
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.GraphDefinition import GraphDefinition

import logging
log = logging.getLogger("zen.migrate")

class SplitOutPsGraphs(ZenPackMigration):
    """
    Process monitoring graphs elsewhere in the system do not have the CPU
    Utilization graph combined with the process count graph. Let's be
    consistent.
    """

    version = Version(1, 3, 9)

    def migrate(self, pack):
        try:
            path = '/zport/dmd/Devices/Server/SSH/Linux/rrdTemplates/OSProcess'
            template = pack.dmd.unrestrictedTraverse(path)
        except:
            log.warn('Unable to find OSProcess template')
        else:
            # Set the description
            description = getattr(template, 'description', None)
            newDescription = "Monitors for OSProcess object"
            if description != newDescription:
                template.description = newDescription

            i = 3
            # Memory graph
            try:
                graph = template.graphDefs._getOb('memory')
                graph.rename('Memory')
                graph.units = "bytes"
                graph.miny = 0
                graph.base = True
                graph.sequence = 2
                graph.graphPoints.mem.rpn = "1024,*"
                graph.graphPoints.mem.lineType = 'AREA'
            except Exception as e:
                log.debug("'memory' graph not found")

            # CPU Utilization graph
            try:
                graph = template.graphDefs._getOb('process performance')
                graph.rename('CPU Utilization')
                graph.graphPoints.cpu.lineType = 'AREA'
                del graph.graphPoints.cpu.rpn
                graph.miny = 0
                graph.sequence = 1
            except Exception as e:
                log.debug("'process performance' graph not found")
            else:
                cpuGraph = graph
                # Process Count graph
                try:
                    graph = template.graphDefs._getOb('Process Count', None)
                    if not graph:
                        log.warn('Creating a Process Count graph')
                        graph = template.manage_addGraphDefinition('Process Count')
                        graph.height = 100
                        graph.width = 500
                        graph.units = "processes"
                        graph.log = False
                        graph.base = False
                        graph.miny = 0
                        graph.maxy = -1
                        graph.hasSummary = True
                        graph.sequence = 3
                        i = 4
                        count = cpuGraph.graphPoints.count
                        count.lineType = 'AREA'
                        count.moveMeBetweenRels(cpuGraph.graphPoints, graph.graphPoints)
                    else:
                        log.warn('meh')
                except Exception as e:
                    log.warn('Failed while creating Process Count graph')

            # Resequence any other graphs, if any.
            for g in template.getGraphDefs():
                if g.id not in ['Memory', 'CPU Utilization', 'Process Count']:
                    g.sequence = i
                    i += 1

SplitOutPsGraphs()
