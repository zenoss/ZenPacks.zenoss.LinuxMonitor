##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
lvm - logical volume manager

Modeling plugin that models logical volumes.  One or more physical volumes
comprise a volume group. A volume group is then split into one or more logical
volumes.
"""

import logging

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.LinuxMonitor.util import LVMAttributeParser
log = logging.getLogger('zen.lvm')


class lvm(CommandPlugin):
    """
    /usr/bin/fdisk -l  | grep '^Disk' | grep -v 'mapper\|identifier\|label' | awk '{gsub(":","");print $2" "$5}'
    /usr/bin/sudo pvs --units b --nosuffix -o pv_name,pv_fmt,pv_attr,pv_size,pv_free,pv_uuid,vg_name;
    /usr/bin/sudo vgs --units b --nosuffix -o vg_name,vg_attr,vg_size,vg_free,vg_uuid;
    /usr/bin/sudo lvs --units b --nosuffix -o lv_name,vg_name,lv_attr,lv_size,lv_uuid,origin

    sample output:
    /dev/sda 21474836480
    /dev/sdb 21474836480
    /dev/sdc 21474836480
    /dev/sdd 21474836480
    PV         Fmt  Attr PSize       PFree       PV UUID                                VG
    /dev/sda2  lvm2 a--  20946354176    41943040 hctl0n-t76R-AdMs-FG1x-IUxG-hbTi-FZlhXG centos
    /dev/sdb1  lvm2 a--  21470642176           0 KN4g1e-iko0-Zn9E-8jkZ-q7oE-cHZO-dEhGM2 fileserver
    /dev/sdc1  lvm2 a--  21470642176  9655287808 ee1vfJ-qMiy-td19-p8re-lrqj-WSGB-xXRUky fileserver
    /dev/sdd1  lvm2 ---  10737418240 10737418240 vgg70r-2swz-iOiy-L8V7-PITB-e4Gy-DkUlMe
    /dev/sdd2  lvm2 ---  10736369664 10736369664 d2FDsD-Y5nV-w7rU-nJL7-qPk0-dskC-3vLOJ0
    VG         #PV #LV #SN Attr   VSize       VFree
    centos       1   2   0 wz--n- 20946354176    41943040
    fileserver   2   3   0 wz--n- 42941284352 15023996928
    LV     VG         Attr       LSize       Active
    root   centos     -wi-ao---- 18756927488 active
    swap   centos     -wi-ao----  2147483648 active
    backup fileserver -wi-ao----  5368709120 active
    media  fileserver -wi-ao----  1073741824 active
    share  fileserver -wi-ao---- 21474836480 active
    """

    command = ('/usr/bin/echo "PD";/usr/bin/sudo /usr/sbin/fdisk -l  | /usr/bin/grep \'^Disk\' | /usr/bin/grep -v '
               '\'mapper\|identifier\|label\' | /usr/bin/awk \'{gsub(":","");print $2" "$5}\'; '
               '/usr/bin/sudo /sbin/pvs --units b --nosuffix -o pv_name,pv_fmt,pv_attr,pv_size,pv_free,pv_uuid,vg_name; '
               '/usr/bin/sudo /sbin/vgs --units b --nosuffix -o vg_name,vg_attr,vg_size,vg_free,vg_uuid; '
               '/usr/bin/sudo /sbin/lvs --units b --nosuffix -o lv_name,vg_name,lv_attr,lv_size,lv_uuid,lv_dm_path,origin')

    def process(self, device, results, log):
        pd_maps = []
        pv_maps = []
        vg_maps = []
        lv_maps = []
        sv_maps = []
        lvm_parser = LVMAttributeParser()
        section = ''
        for line in results.split('\n'):
            columns = line.split()
            if not columns:
                continue
            if columns[0] in ['PD', 'PV', 'VG', 'LV']:
                section = columns[0]
                continue
            if section == 'PD':
                pd_om = ObjectMap()
                pd_om.title = columns[0]
                pd_om.id = self.prepId(columns[0])
                pd_om.size = int(columns[1])
                pd_om.relname = 'physicalDisks'
                pd_om.modname = 'ZenPacks.zenoss.LinuxMonitor.PhysicalDisk'
                pd_maps.append(pd_om)
            elif section == 'PV':
                pv_om = ObjectMap()
                pv_om.title = columns[0]
                pv_om.id = self.prepId(columns[0])
                pv_om.format = columns[1]
                pv_om.attributes = lvm_parser.pv_attributes(columns[2])
                pv_om.pvsize = int(columns[3])
                pv_om.free = int(columns[4])
                pv_om.uuid = columns[5]
                if len(columns) == 7:
                    pv_om.set_volumeGroup = columns[6]
                pv_om.relname = 'physicalVolumes'
                pv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume'
                for pd_om in pd_maps:
                    if pd_om.title in pv_om.title:
                        pv_om.set_physicalDisk = pd_om.id
                pv_maps.append(pv_om)
            elif section == 'VG':
                vg_om = ObjectMap()
                vg_om.title = columns[0]
                vg_om.id = self.prepId(columns[0])
                vg_om.attributes = lvm_parser.vg_attributes(columns[1])
                vg_om.vgsize = int(columns[2])
                vg_om.freesize = int(columns[3])
                vg_om.uuid = columns[4]
                vg_om.relname = 'volumeGroups'
                vg_om.modname = 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup'
                vg_maps.append(vg_om)
            elif section == 'LV':
                lv_om = ObjectMap()
                lv_om.title = columns[0]
                lv_om.vgname = columns[1]
                lv_om.id = self.prepId(columns[1]+'_'+columns[0])
                lv_om.attributes = lvm_parser.lv_attributes(columns[2])
                lv_om.lvsize = int(columns[3])
                lv_om.active = True if 'active' in lv_om.attributes else False
                lv_om.uuid = columns[4]
                lv_om.dm_path = columns[5]
                if len(columns) == 7:
                    lv_om.origin = columns[6]
                    lv_om.relname = 'snapshotVolumes'
                    lv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.SnapshotVolume'
                    sv_maps.append(lv_om)
                else:
                    lv_om.relname = 'logicalVolumes'
                    lv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.LogicalVolume'
                    lv_maps.append(lv_om)

        maps = []
        maps.append(RelationshipMap(
            relname="volumeGroups",
            modname="ZenPacks.zenoss.LinuxMonitor.VolumeGroup",
            objmaps=vg_maps))

        maps.append(RelationshipMap(
            relname='physicalDisks',
            modname="ZenPacks.zenoss.LinuxMonitor.PhysicalDisk",
            objmaps=pd_maps))

        maps.append(RelationshipMap(
            relname="physicalVolumes",
            modname="ZenPacks.zenoss.LinuxMonitor.PhysicalVolume",
            objmaps=pv_maps))

        for vg_om in vg_maps:
            lv_vg_oms = []
            compname = 'volumeGroups/' + vg_om.id
            for lv_om in lv_maps:
                if lv_om.vgname == vg_om.title:
                    lv_vg_oms.append(lv_om)
            maps.append(RelationshipMap(
                relname="logicalVolumes",
                compname=compname,
                modname="ZenPacks.zenoss.LinuxMonitor.LogicalVolume",
                objmaps=lv_vg_oms))

            for lv_om in lv_maps:
                if lv_om.vgname == vg_om.title:
                    lv_sv_oms = []
                    for sv_om in sv_maps:
                        if sv_om.origin == lv_om.title:
                            lv_sv_oms.append(sv_om)
                    maps.append(RelationshipMap(
                        relname="snapshotVolumes",
                        compname=compname + '/logicalVolumes/' + lv_om.id,
                        modname="ZenPacks.zenoss.LinuxMonitor.SnapshotVolume",
                        objmaps=lv_sv_oms))
        return maps
