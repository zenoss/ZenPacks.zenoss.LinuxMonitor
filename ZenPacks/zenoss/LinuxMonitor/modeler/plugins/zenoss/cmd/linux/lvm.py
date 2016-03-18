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
import re

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
    HD
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
    NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
    fd0 2:0 1 4096 0 disk
    sda 8:0 0 21474836480 0 disk
    sda1 8:1 0 524288000 0 part /boot
    sda2 8:2 0 20949499904 0 part
    centos-root 253:0 0 18756927488 0 lvm /
    centos-swap 253:1 0 2147483648 0 lvm [SWAP]
    sdb 8:16 0 21474836480 0 disk
    sdb1 8:17 0 21473787904 0 part
    fileserver-share-real 253:2 0 21474836480 0 lvm
    fileserver-share 253:3 0 21474836480 0 lvm /var/share
    fileserver-snap 253:5 0 21474836480 0 lvm
    sdc 8:32 0 21474836480 0 disk
    sdc1 8:33 0 21473787904 0 part
    fileserver-share-real 253:2 0 21474836480 0 lvm
    fileserver-share 253:3 0 21474836480 0 lvm /var/share
    fileserver-snap 253:5 0 21474836480 0 lvm
    fileserver-snap-cow 253:4 0 5368709120 0 lvm
    fileserver-snap 253:5 0 21474836480 0 lvm
    fileserver-backup 253:6 0 5368709120 0 lvm /var/backup
    fileserver-media 253:7 0 1073741824 0 lvm /var/media
    fileserver-inactive 253:8 0 5368709120 0 lvm
    sdd 8:48 0 21474836480 0 disk
    sdd1 8:49 0 21473787904 0 part
    sr0 11:0 1 63019008 0 rom

    MAJ:MIN can be used for diskstats
    """

    command = ('lsblk -rb 2>&1; '
               'sudo pvs --units b --nosuffix -o pv_name,pv_fmt,pv_attr,pv_size,pv_free,pv_uuid,vg_name 2>&1; '
               'sudo vgs --units b --nosuffix -o vg_name,vg_attr,vg_size,vg_free,vg_uuid 2>&1; '
               'sudo lvs --units b --nosuffix -o lv_name,vg_name,lv_attr,lv_size,lv_uuid,origin 2>&1 ')

    def process(self, device, results, log):
        hd_maps = []
        pv_maps = []
        vg_maps = []
        lv_maps = []
        sv_maps = []
        lsblk_dict = {}
        self.lvm_parser = LVMAttributeParser()
        section = ''
        hd_re = re.compile('(?P<disk>\S+) (?P<size>\d+)')
        dev_blk_re = re.compile('(?P<device_block>.*)\s+(?P<major_minor>\d+:\d+)\s+\d+\s+(?P<size>\d+)\s+\d+\s+(?P<type>\w+)\s*(?P<mount>\S*)')
        pv_re = re.compile('\s*(?P<pv_name>\S+)\s*(?P<pv_fmt>\S+)\s*(?P<pv_attr>\S+)\s*(?P<pv_size>\S+)'
                           '\s*(?P<pv_free>\S+)\s*(?P<pv_uuid>\S+)\s*(?P<vg_name>\S*)')
        vg_re = re.compile('\s*(?P<vg_name>\S+)\s*(?P<vg_attr>\S+)\s*(?P<vg_size>\S+)\s*(?P<vg_free>\S+)\s*(?P<vg_uuid>\S+)')
        lv_re = re.compile('\s*(?P<lv_name>\S+)\s*(?P<vg_name>\S+)\s*(?P<lv_attr>\S+)\s*(?P<lv_size>\S+)\s*(?P<lv_uuid>\S+)\s*(?P<origin>\S*)')
        parse_re = {'HD': hd_re, 'PV': pv_re, 'VG': vg_re, 'LV': lv_re, 'NAME': dev_blk_re}
        for line in results.split('\n'):
            if self.checkErr(line):
                return []
            res = line.split()
            if not res:
                continue
            if res[0] in parse_re.keys():
                section = res[0]
                continue
            try:
                columns = parse_re[section].match(line).groupdict()
            except (AttributeError, Exception):
                continue

            if section == 'PV':
                pv_om = self.makePVMap(columns)
                pv_maps.append(pv_om)
                for hd_om in hd_maps:
                    if hd_om.title == pv_om.title.split('/')[-1]:
                        pv_om.harddisk_id = hd_om.id
            elif section == 'VG':
                vg_maps.append(self.makeVGMap(columns))
            elif section == 'LV':
                lv_om = self.makeLVMap(columns)
                if lv_om.relname == 'snapshotVolumes':
                    sv_maps.append(lv_om)
                else:
                    lv_maps.append(lv_om)
            elif section == 'NAME':
                # device block can be 'vg_name-lv_name' or 'vg_name-lv_name (DM-X)' format
                # depending on linux flavor
                columns = {col[0]: col[1].strip() for col in columns.items()}
                device_block = columns['device_block'].split()[0]
                lsblk_dict[device_block] = {}
                lsblk_dict[device_block]['mount'] = columns['mount']
                lsblk_dict[device_block]['major_minor'] = columns['major_minor']
                if any(columns['device_block'] == om.title for om in hd_maps):
                    continue
                if columns['type'] in ('disk', 'lvm', 'part', 'raid1'):
                    hd_maps.append(self.makeHDMap(columns))

        maps = []
        maps.append(RelationshipMap(
            relname="volumeGroups",
            modname="ZenPacks.zenoss.LinuxMonitor.VolumeGroup",
            objmaps=vg_maps))

        maps.append(RelationshipMap(
            compname='hw',
            relname='harddisks',
            modname="ZenPacks.zenoss.LinuxMonitor.HardDisk",
            objmaps=hd_maps))

        maps.append(RelationshipMap(
            relname="physicalVolumes",
            modname="ZenPacks.zenoss.LinuxMonitor.PhysicalVolume",
            objmaps=pv_maps))

        for vg_om in vg_maps:
            lv_vg_oms = []
            compname = 'volumeGroups/' + vg_om.id
            for lv_om in lv_maps:
                if lv_om.vgname == vg_om.title:
                    # LVM delimits VG-LV with a hyphen. To unambiguously handle
                    # LVs and VGs with hyphens in their name, it doubles
                    # hypens in the LV and VG names. We have to do the same.
                    device_block = '{}-{}'.format(
                        lv_om.vgname.replace('-', '--'),
                        lv_om.title.replace('-', '--'))

                    try:
                        lv_om.mountpoint = lsblk_dict[device_block]['mount']
                        lv_om.major_minor = lsblk_dict[device_block]['major_minor']
                    except KeyError:
                        # device block not found
                        log.debug('device block {} not found for logical volume {} in volume group {}'
                                  .format(lv_om.vgname+'-'+lv_om.title, lv_om.title, lv_om.vgname))
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
                            device_block = '{}-{}'.format(
                                sv_om.vgname.replace('-', '--'),
                                sv_om.title.replace('-', '--'))
                            try:
                                sv_om.mountpoint = lsblk_dict[device_block]['mount']
                                sv_om.major_minor = lsblk_dict[device_block]['major_minor']
                            except KeyError:
                                # device block not found
                                log.debug('device block {} not found for snapshot volume {} in volume group {}'
                                          .format(sv_om.vgname+'-'+sv_om.title, sv_om.title, sv_om.vgname))
                            lv_sv_oms.append(sv_om)
                    maps.append(RelationshipMap(
                        relname="snapshotVolumes",
                        compname=compname + '/logicalVolumes/' + lv_om.id,
                        modname="ZenPacks.zenoss.LinuxMonitor.SnapshotVolume",
                        objmaps=lv_sv_oms))
        return maps

    def makeHDMap(self, columns):
        hd_om = ObjectMap()
        hd_om.title = columns['device_block']
        hd_om.id = 'disk-{}'.format(self.prepId(
            columns['device_block'].replace(' ', '_')))
        hd_om.major_minor = columns['major_minor']
        hd_om.mount = columns['mount']
        hd_om.size = int(columns['size'])
        hd_om.relname = 'harddisks'
        hd_om.modname = 'ZenPacks.zenoss.LinuxMonitor.HardDisk'
        return hd_om

    def makePVMap(self, columns):
        # pv_name,pv_fmt,pv_attr,pv_size,pv_free,pv_uuid,vg_name
        pv_om = ObjectMap()
        pv_om.title = columns['pv_name']
        pv_om.id = 'pv-{}'.format(self.prepId(columns['pv_name']))
        pv_om.format = columns['pv_fmt']
        pv_om.attributes = self.lvm_parser.pv_attributes(columns['pv_attr'])
        pv_om.uuid = columns['pv_uuid']
        pv_om.set_volumeGroup = 'vg-{}'.format(columns['vg_name']) if columns['vg_name'] else ''
        pv_om.relname = 'physicalVolumes'
        pv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume'
        return pv_om

    def makeVGMap(self, columns):
        # vg_name,vg_attr,vg_size,vg_free,vg_uuid
        vg_om = ObjectMap()
        vg_om.title = columns['vg_name']
        vg_om.id = 'vg-{}'.format(self.prepId(columns['vg_name']))
        vg_om.attributes = self.lvm_parser.vg_attributes(columns['vg_attr'])
        vg_om.uuid = columns['vg_uuid']
        vg_om.relname = 'volumeGroups'
        vg_om.modname = 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup'
        return vg_om

    def makeLVMap(self, columns):
        # lv_name,vg_name,lv_attr,lv_size,lv_uuid,origin
        lv_om = ObjectMap()
        lv_om.title = columns['lv_name']
        lv_om.vgname = columns['vg_name']
        lv_om.id = 'lv-{}'.format(self.prepId(columns['vg_name'])+'_'+self.prepId(columns['lv_name']))
        lv_om.attributes = self.lvm_parser.lv_attributes(columns['lv_attr'])
        lv_om.lvsize = int(columns['lv_size'])
        lv_om.uuid = columns['lv_uuid']
        if columns['origin']:
            lv_om.origin = columns['origin']
            lv_om.relname = 'snapshotVolumes'
            lv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.SnapshotVolume'
        else:
            lv_om.relname = 'logicalVolumes'
            lv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.LogicalVolume'
        return lv_om

    def checkErr(self, line):
        if 'no tty present' in line or 'sudo: sorry, you must have a tty to run sudo' in line:
            log.warning('No tty present.  Ensure that user is sudo and change sudo settings to disable requiretty for your user account.')
            return True
        return False
