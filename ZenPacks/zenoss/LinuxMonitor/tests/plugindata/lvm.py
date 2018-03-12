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
        {'vg-lvmserver':
            {'attributes': ['writeable', 'resizable', 'normal'],
             'id': 'vg-lvmserver',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup',
             'relname': 'volumeGroups',
             'title': 'lvmserver',
             'uuid': 'RRYHWp-twqJ-x89e-1WXs-iDFu-R2EE-5KPL4d'}, },
        {'disk-sda':
            {'disk_ids': ['ata-3.14159', 'scsi-3.14159'],
             'id': 'disk-sda',
             'major_minor': '8:0',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.HardDisk',
             'mount': '',
             'relname': 'harddisks',
             'size': 21474836480,
             'title': 'sda'}, },
        {'pv-dev_sda5':
            {'attributes': ['allocatable'],
             'format': 'lvm2',
             'id': 'pv-dev_sda5',
             'modname': 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume',
             'relname': 'physicalVolumes',
             'set_volumeGroup': 'vg-qa-ubuntu-12',
             'title': '/dev/sda5',
             'uuid': 'keTXxa-Jlrw-0FJS-b2ye-iP15-fgsF-KavDVv'}, },
        {'lv-lvmserver_share':
            {'attributes': ['writeable', 'inherited', 'active', 'open'],
             'id': 'lv-lvmserver_share',
             'lvsize': 10737418240,
             'modname': 'ZenPacks.zenoss.LinuxMonitor.LogicalVolume',
             'relname': 'logicalVolumes',
             'title': 'share',
             'uuid': 'SBIYpJ-Xgcr-0nlT-ModL-aqev-1L2T-rQgZUX',
             'vgname': 'lvmserver'}, },

        {'lv-lvmserver_share-snapshot':
            {'attributes': ['snapshot', 'writeable', 'inherited', 'active'],
             'id': 'lv-lvmserver_share-snapshot',
             'lvsize': 2147483648,
             'modname': 'ZenPacks.zenoss.LinuxMonitor.SnapshotVolume',
             'origin': 'share',
             'relname': 'snapshotVolumes',
             'title': 'share-snapshot',
             'uuid': 'LnFf8w-BUSe-1JNo-9Y07-Colf-ztAX-N8ih65',
             'vgname': 'lvmserver'}, },
        {'lv-lvmserver_pool':
            {'attributes': ['thin pool','writeable','inherited','active','open','thin'],
             'id': 'lv-lvmserver_pool',
             'lvsize': 1073741824,
             'modname': 'ZenPacks.zenoss.LinuxMonitor.ThinPool',
             'lv_metadata_size': '4194304',
             'relname': 'thinPools',
             'title': 'pool',
             'uuid': 'Je2mF8-V0q3-CXVX-6p21-eBAD-VMPt-pEOczH',
             'vgname': 'lvmserver'}, },
    ]}
