##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from . import zenpacklib
import os.path
from Products.CMFCore.DirectoryView import registerDirectory

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

# CFG is necessary when using zenpacklib.TestCase.
CFG = zenpacklib.load_yaml()

# Patch last to avoid import recursion problems.
from ZenPacks.zenoss.LinuxMonitor import patches  # NOQA
