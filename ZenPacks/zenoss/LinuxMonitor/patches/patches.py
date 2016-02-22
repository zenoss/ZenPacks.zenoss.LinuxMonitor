##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenUtils.Utils import monkeypatch
from Products.Zuul import getFacade


@monkeypatch('Products.ZenModel.Device.Device')
def getPingStatus(self):
    def monitored_with_ssh(device):
        for template in device.getRRDTemplates():
            for datasource in template.datasources():
                if datasource.sourcetype == 'COMMAND' and datasource.usessh:
                    return True

        return False
    if monitored_with_ssh(self):
        zep = getFacade('zep')
        fltr = zep.createEventFilter(element_identifier=self.id,
                                     event_class=('/Cmd/Fail', '/Status/Ping'),
                                     severity=(4, 5), status=(0, 1, 2))
        events = zep.getEventSummaries(0, filter=fltr)
        try:
            events['events'].next()
            return 1
        except StopIteration:
            return 0
    else:
        return original(self)
