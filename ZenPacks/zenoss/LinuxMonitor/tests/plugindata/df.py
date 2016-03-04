##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

{'df':
    [
        {'-':
            {'blockSize': 1024,
             'classname': '',
             'compname': 'os',
             'id': '-',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.FileSystem',
             'mount': '/',
             'storageDevice': '/dev/mapper/centos-root',
             'title': '/',
             'totalBlocks': 49746196L,
             'type': 'xfs'}, },
        {'dev':
            {'blockSize': 1024,
             'classname': '',
             'compname': 'os',
             'id': 'dev',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.FileSystem',
             'mount': '/dev',
             'storageDevice': 'devtmpfs',
             'title': '/dev',
             'totalBlocks': 1931008L,
             'type': 'devtmpfs'}, },

        {'dev_shm':
            {'blockSize': 1024,
             'classname': '',
             'compname': 'os',
             'id': 'dev_shm',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.FileSystem',
             'mount': '/dev/shm',
             'storageDevice': 'tmpfs',
             'title': '/dev/shm',
             'totalBlocks': 1941228L,
             'type': 'tmpfs'}, },
        {'run':
            {'blockSize': 1024,
             'classname': '',
             'compname': 'os',
             'id': 'run',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.FileSystem',
             'mount': '/run',
             'storageDevice': 'tmpfs',
             'title': '/run',
             'totalBlocks': 1941228L,
             'type': 'tmpfs'}, },
        {'sys_fs_cgroup':
            {'blockSize': 1024,
             'classname': '',
             'compname': 'os',
             'id': 'sys_fs_cgroup',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.FileSystem',
             'mount': '/sys/fs/cgroup',
             'storageDevice': 'tmpfs',
             'title': '/sys/fs/cgroup',
             'totalBlocks': 1941228L,
             'type': 'tmpfs'}, }
    ]}
