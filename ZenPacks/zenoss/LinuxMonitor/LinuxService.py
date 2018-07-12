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


class LinuxService(schema.LinuxService):

    """Model class for Linux OS Service."""

    def getRRDTemplates(self):
        all_templates = super(LinuxService, self).getRRDTemplates()
        used_templates = []
        if not self.init_system:
            return used_templates
        for template in all_templates:
            if self.init_system in template.id:
                used_templates.append(template)
        return used_templates
