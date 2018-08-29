##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


"""LinuxService module.

All custom behavior for Linux OS Service is defined here.

"""


from . import schema
from . import MODELER_VERSION_PROPERTY
from . import OS_SERVICE_MODELER_VERSION


class LinuxService(schema.LinuxService):

    """Model class for Linux OS Service."""

    def getModelerVersion(self):
        """Return version of modeler plugin that modeled this component, or 0 if unknown."""
        if self.aqBaseHasAttr(MODELER_VERSION_PROPERTY):
            try:
                return int(getattr(self, MODELER_VERSION_PROPERTY))
            except Exception:
                return 0

        return 0

    def getRRDTemplates(self):
        """Return list of monitoring templates to use for this component."""
        all_templates = super(LinuxService, self).getRRDTemplates()

        # We don't know the init system, so we don't know how to monitor it.
        if not self.init_system:
            return []

        # We were modeled with too old of a modeler plugin. Monitoring would be unsafe.
        if self.getModelerVersion() < OS_SERVICE_MODELER_VERSION:
            return []

        used_templates = []
        for template in all_templates:
            if self.init_system in template.id:
                used_templates.append(template)

        return used_templates
