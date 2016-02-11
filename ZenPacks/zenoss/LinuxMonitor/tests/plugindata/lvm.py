##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
{'lvm':
    [
        {'centos':
            {'attributes': ['resizable', 'exported', 'partial'],
             'freesize': 0,
             'id': 'centos',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup',
             'relname': 'volumeGroups',
             'title': 'centos',
             'uuid': 'wz--n-',
             'vgsize': 2},
         'fileserver':
            {'attributes': ['resizable', 'exported', 'partial'],
             'freesize': 0,
             'id': 'fileserver',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup',
             'relname': 'volumeGroups',
             'title': 'fileserver',
             'uuid': 'wz--n-',
             'vgsize': 3}, },
        {'dev_sda2':
            {'attributes': ['allocatable'],
             'format': 'lvm2',
             'free': 41943040,
             'id': 'dev_sda2',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume',
             'pvsize': 20946354176,
             'relname': 'physicalVolumes',
             'set_volumeGroup': 'centos',
             'title': '/dev/sda2',
             'uuid': 'hctl0n-t76R-AdMs-FG1x-IUxG-hbTi-FZlhXG'},
         'dev_sdb1':
            {'attributes': ['allocatable'],
             'format': 'lvm2',
             'free': 0,
             'id': 'dev_sdb1',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume',
             'pvsize': 21470642176,
             'relname': 'physicalVolumes',
             'set_volumeGroup': 'fileserver',
             'title': '/dev/sdb1',
             'uuid': 'KN4g1e-iko0-Zn9E-8jkZ-q7oE-cHZO-dEhGM2'}, },
        {'centos_root':
            {'active': True,
             'attributes': ['writeable', 'inherited', 'active', 'open'],
             'id': 'centos_root',
             'lvsize': 18756927488,
             'modname': 'ZenPacks.zenoss.LinuxMonitor.LogicalVolume',
             'relname': 'logicalVolumes',
             'title': 'root',
             'uuid': 'active',
             'vgname': 'centos'}, }
    ]}
