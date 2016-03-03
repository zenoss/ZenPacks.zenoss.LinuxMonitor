##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import collections

from Products.ZenUtils.Utils import getObjectsFromCatalog, monkeypatch
from Products.Zuul.facades.devicefacade import DeviceFacade

from ZenPacks.zenoss.LinuxMonitor.LinuxDevice import LinuxDevice


if hasattr(DeviceFacade, "getGraphDefinitionsForComponent"):
    @monkeypatch(DeviceFacade)
    def getGraphDefinitionsForComponent(self, *args, **kwargs):
        """Return dictionary of meta_type to associated graph definitions.

        component.getGraphObjects() can return pairs of (graphDef, context)
        where context is not the component. One example is
        FileSystem.getGraphObjects returning pairs for graphs on its underlying
        HardDisk. We have to make sure to return these graph definitions under
        their meta_type, not component's meta_type.

        We accept *args and **kwargs to be less brittle in case the
        monkeypatched method changes signature in an otherwise unaffecting way.

        args is expected to look something like this:

            ('/zport/dmd/Devices/Server/SSH/Linux/devices/centos-7',)

        kwargs is expected to look like this:

            {}

        """
        obj = self._getObject(args[0])

        # Limit the patch scope to this ZenPack even though it'd probably be a
        # good idea for everything.
        if not isinstance(obj, LinuxDevice):
            return original(self, *args, **kwargs)  # NOQA

        graphDefs = collections.defaultdict(set)
        for component in getObjectsFromCatalog(obj.componentSearch):
            for graphDef, context in component.getGraphObjects():
                graphDefs[context.meta_type].add(graphDef.id)

        return graphDefs
