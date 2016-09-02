##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014-2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
import twisted
from importlib import import_module
from pkg_resources import parse_version

LOG = logging.getLogger('zen.LinuxMonitor')


def optional_import(module_name, patch_module_name):
    """Import patch_module_name only if module_name is importable."""
    try:
        import_module(module_name)
    except ImportError:
        pass
    else:
        try:
            import_module(
                '.{0}'.format(patch_module_name),
                'ZenPacks.zenoss.LinuxMonitor.patches')
        except ImportError:
            LOG.exception("failed to apply %s patches", patch_module_name)


optional_import('Products.ZenModel', 'platform')

# We only need to patch Conch in Twisted versions earlier than 15.
if parse_version(twisted.__version__) < parse_version("15"):
    optional_import('twisted.conch', 'twistedConch')
