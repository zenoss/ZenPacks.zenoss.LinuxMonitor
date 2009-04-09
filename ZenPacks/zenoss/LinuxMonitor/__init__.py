###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
import Globals
import os.path
from Products.ZenModel.ZenPack import ZenPackBase

log = logging.getLogger('zen.LinuxMonitor')

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

def findLinux(dmd):
    return dmd.findChild('Devices/Server/SSH/Linux')

class ZenPack(ZenPackBase):
    
    def install(self, app):
        """
        Set the collector plugins for Server/SSH/Linux.
        """
        try:
            linux = findLinux(app.dmd)
        except Exception, e:
            import traceback
            log.debug(traceback.format_exc())
            raise Exception('Device class Server/SSH/Linux does not exist. '
                            'Cannot install LinuxMonitor ZenPack.')
        ZenPackBase.install(self, app)
        linux.setZenProperty( 'zCollectorPlugins', 
                              ['zenoss.cmd.uname',
                               'zenoss.cmd.uname_a',
                               'zenoss.cmd.df',
                               'zenoss.cmd.linux.cpuinfo'] )
                                   
    def remove(self, app, leaveObjects=False):
        """
        Remove the collector plugins.
        """
        ZenPackBase.remove(self, app, leaveObjects)
        if not leaveObjects:
            findLinux(app.dmd).zCollectorPlugins = []
            
