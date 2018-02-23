##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""dpkg
Modeler plugin

    Commands:

      'export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin; '
      'if command -v dpkg; then '
      'for file_list in `ls /var/lib/dpkg/info/*.list`; '
      'do stat_result=$(stat --format=%Y "$file_list"); '
      'printf "%s %s\n"_field:$(basename $file_list .list) "_field:$stat_result"; '
      'done; '
      'dpkg-query -W -f=\'_field:${Package}_field:${Version}_field:${Maintainer}_field:${Description}\n\'; '
      'fi '

    Properties:

        os.software: productKey, description, installDate


    Example command output:

        _field:zenity-common_field:1503514995
        _field:zenity_field:1503514082
        _field:zlib1g:amd64
        _field:zenity_field:3.22.0-1+b1_field:Debian GNOME Maintainers <pkg-gnome-maintainers@lists.alioth.debian.org>_field:Display graphical dialog boxes from shell scripts
         Zenity allows you to display GTK+ dialogs from shell scripts; it is a
         rewrite of the `gdialog' command from GNOME 1.
         .
         Zenity includes a gdialog wrapper script so that it can be used with
         legacy scripts.
        _field:zenity-common_field:3.22.0-1_field:Debian GNOME Maintainers <pkg-gnome-maintainers@lists.alioth.debian.org>_field:Display graphical dialog boxes from shell scripts (common files)
         Zenity allows you to display GTK+ dialogs from shell scripts; it is a
         rewrite of the `gdialog' command from GNOME 1.
         .
         Zenity includes a gdialog wrapper script so that it can be used with
         legacy scripts.
         .
         This package contains architecture independent files.
        _field:zlib1g_field:1:1.2.8.dfsg-5_field:Mark Brown <broonie@debian.org>_field:compression library - runtime
         zlib is a library implementing the deflate compression method found
         in gzip and PKZIP.  This package includes the shared library.

    ...

"""

import logging
from time import gmtime

import Products.DataCollector.CommandPluginUtils as utils

from Products.DataCollector.plugins.CollectorPlugin \
        import SoftwareCommandPlugin


log = logging.getLogger("zen.dpkg")
main_vendors = ('debian','ubuntu')


def getVendor(maintainer):
    for vendor in main_vendors:
        if vendor in maintainer.lower():
            return vendor.capitalize()
    return maintainer.split(' <')[0]

def parseResults(results):
    """
    Parse the results of the dpkg command to create a dictionary of installed
    software.
    """
    timeDict = {}
    softwareDicts = []
    for line in results.splitlines():
        line = line.split('_field:')[1:]
        if len(line) == 2:
            timeDict[line[0]] = gmtime(int(line[1]))
        elif line and '' not in line and line[0] in timeDict:
            softwareDicts.append(utils.createSoftwareDict(
                    line[0] + '-' + line[1],
                    getVendor(line[2]),
                    line[3],
                    timeDict[line[0]]))
    return softwareDicts


class dpkg(SoftwareCommandPlugin):
    """
    Parse dpkg to get installed software.
    """

    command = ('export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin; '
               'if command -v dpkg; then '
               'for file_list in `ls /var/lib/dpkg/info/*.list`; '
               'do stat_result=$(stat --format=%Y "$file_list"); '
               'printf "%s %s\n"_field:$(basename $file_list .list) "_field:$stat_result"; '
               'done; '
               'dpkg-query -W -f=\'_field:${Package}_field:${Version}_field:${Maintainer}_field:${Description}\n\'; '
               'fi '
              )
    def __init__(self):
        """
        Initialize this SoftwareCommandPlugin with the parseResults function
        from this module.
        """
        SoftwareCommandPlugin.__init__(self, parseResults)
