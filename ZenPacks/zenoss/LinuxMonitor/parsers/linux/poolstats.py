##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Parse results of lvm2 "lvs" command.

Retrieve the data_percent and metadata_percent fields.

sample output:
docker   docker-pool   6.85   1.35
serviced serviced-pool 4.94   0.56


"""
import logging
log = logging.getLogger("zen.poolstats")

from Products.ZenRRD.CommandParser import CommandParser

class poolstats(CommandParser):

    def dataForParser(self, context, dp):
        """Add additional data to dp for the processResults method.

        This method is executed in zenhub, so context will be a full
        ThinPool.

        """
        return {
            'vgname': getattr(context, 'vgname', None),
            'lvname': getattr(context, 'title', None),
            }

    def processResults(self, cmd, result):

        for dp in cmd.points:

            for line in cmd.result.output.split('\n'):
                try:
                    vg_name, lv_name, data_percent, metadata_percent = line.strip().split()
                except ValueError:
                    continue

                # Verify that this line is for the appropriate component.
                if vg_name != dp.data['vgname'] or lv_name != dp.data['lvname']:
                    continue

                if dp.id == 'percentDataUsed':
                    result.values.append((dp, data_percent))
                elif dp.id == 'percentMetaDataUsed':
                    result.values.append((dp, metadata_percent))
        return result
