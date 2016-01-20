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
    if self.path()[0][6] == 'Linux':
        zep = getFacade('zep')
        fltr = zep.createEventFilter(element_identifier=self.id,
                                     event_class=('/Cmd/Fail', '/Status/Ping'),
                                     severity=(4, 5), status=(0, 1, 2))
        events = zep.getEventSummaries(0, filter=fltr)
        try:
            events['events'].next()
            return 1
        except StopIteration, e:
            return 0
    else:
        return original(self)
