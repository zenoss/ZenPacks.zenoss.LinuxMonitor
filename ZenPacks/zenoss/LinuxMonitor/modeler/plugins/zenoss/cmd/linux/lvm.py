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
log = logging.getLogger('zen.lvm')


class lvm(CommandPlugin):
    """
    /sbin/pvdisplay; /sbin/vgdisplay; /sbin/lvdisplay - get LVM information on Linux machines

    sample output:
    PV         VG         Fmt  Attr PSize       PFree
    /dev/sda2  centos     lvm2 a--  20946354176    41943040
    /dev/sdb1  fileserver lvm2 a--  21470642176           0
    /dev/sdc1  fileserver lvm2 a--  21470642176 15023996928
    /dev/sdd1             lvm2 ---  10737418240 10737418240
    /dev/sdd2             lvm2 ---  10736369664 10736369664
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

    command = ('/usr/bin/sudo pvs --units b --nosuffix -o pv_name,vg_name,pv_fmt,pv_attr,pv_size,pv_free,pv_uuid; '
               '/usr/bin/sudo vgs --units b --nosuffix -o vg_name,vg_attr,vg_size,vg_free,vg_uuid; '
               '/usr/bin/sudo lvs --units b --nosuffix -o lv_name,vg_name,lv_attr,lv_size,lv_uuid,origin')

    def process(self, device, results, log):
        vg_maps = []
        pv_maps = []
        lv_maps = []
        sv_maps = []
        for line in results.split('\n'):
            columns = line.split()
            if not columns:
                continue
            if columns[0] == 'PV':
                inPV = True
                inVG = False
                inLV = False
                continue
            elif columns[0] == 'VG':
                inVG = True
                inPV = False
                inLV = False
                continue
            elif columns[0] == 'LV':
                inLV = True
                inVG = False
                inPV = False
                continue
            if inPV:
                if len(columns) < 7:
                    # physical volume probably not part of a vg.  ignore for now
                    continue
                pv_om = ObjectMap()
                pv_om.title = columns[0]
                pv_om.vgname = columns[1]
                pv_om.format = columns[2]
                pv_om.attributes = self.pv_attributes(columns[3])
                pv_om.pvsize = int(columns[4])
                pv_om.free = int(columns[5])
                pv_om.util = float(pv_om.pvsize - pv_om.free)/pv_om.pvsize
                pv_om.id = self.prepId(columns[0])
                pv_om.relname = 'physicalVolumes'
                pv_om.modname = 'ZenPacks.zenoss.LinuxMonitor.PhysicalVolume'
                pv_maps.append(pv_om)
            elif inVG:
                vg_om = ObjectMap()
                vg_om.title = columns[0]
                vg_om.attributes = self.vg_attributes(columns[1])
                vg_om.vgsize = int(columns[2])
                vg_om.freesize = int(columns[3])
                vg_om.id = self.prepId(columns[0])
                vg_om.uuid = columns[4]
                vg_om.util = float(vg_om.vgsize - vg_om.freesize)/vg_om.vgsize
                vg_om.relname = 'volumeGroups'
                vg_om.modname = 'ZenPacks.zenoss.LinuxMonitor.VolumeGroup'
                vg_maps.append(vg_om)
            elif inLV:
                lv_om = ObjectMap()
                lv_om.title = columns[0]
                lv_om.vgname = columns[1]
                lv_om.attributes = self.lv_attributes(columns[2])
                lv_om.lvsize = int(columns[3])
                lv_om.active = True if 'active' in lv_om.attributes else False
                lv_om.id = self.prepId(columns[1]+'_'+columns[0])
                lv_om.uuid = self.prepId(columns[4])
                if len(columns) >= 6:
                    lv_om.origin = columns[5]
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

        for vg_om in vg_maps:
            pv_vg_oms = []
            lv_vg_oms = []
            sv_vg_oms = []
            for pv_om in pv_maps:
                if pv_om.vgname == vg_om.title:
                    pv_vg_oms.append(pv_om)
            maps.append(RelationshipMap(
                relname="physicalVolumes",
                compname='volumeGroups/' + vg_om.id,
                modname="ZenPacks.zenoss.LinuxMonitor.PhysicalVolume",
                objmaps=pv_vg_oms))

            # import pdb; pdb.set_trace()
            for sv_om in sv_maps:
                if sv_om.vgname == vg_om.title:
                    sv_vg_oms.append(sv_om)
            maps.append(RelationshipMap(
                relname="snapshotVolumes",
                compname='volumeGroups/' + vg_om.id,
                modname="ZenPacks.zenoss.LinuxMonitor.SnapshotVolume",
                objmaps=sv_vg_oms))

            for lv_om in lv_maps:
                if lv_om.vgname == vg_om.title:
                    lv_vg_oms.append(lv_om)
            maps.append(RelationshipMap(
                relname="logicalVolumes",
                compname='volumeGroups/' + vg_om.id,
                modname="ZenPacks.zenoss.LinuxMonitor.LogicalVolume",
                objmaps=lv_vg_oms))
            for lv_om in lv_maps:
                if lv_om.vgname == vg_om.title:
                    lv_sv_oms = []
                    for sv_om in sv_maps:
                        if sv_om.origin == lv_om.title:
                            sv_om.set_logicalVolume = lv_om.id
                            lv_sv_oms.append(sv_om)
                    if lv_sv_oms:
                        maps.append(RelationshipMap(
                            relname="snapshotVolumes",
                            compname='volumeGroups/' + vg_om.id,
                            modname="ZenPacks.zenoss.LinuxMonitor.SnapshotVolume",
                            objmaps=lv_sv_oms))

        return maps

    def pv_attributes(self, atts):
        # (a)llocatable, e(x)ported and (m)issing
        attributes = []
        if atts[0] == 'a':
            attributes.append('allocatable')
        if atts[1] == 'x':
            attributes.append('exported')
        if atts[2] == 'm':
            attributes.append('missing')
        return attributes

    def lv_attributes(self, atts):
        attributes = []
        attribute = self.lv_volume_type(atts[0])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_permissions(atts[1])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_allocation_policy(atts[2])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_state(atts[4])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_device(atts[5])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_target_type(atts[6])
        if attribute:
            attributes.append(attribute)
        attribute = self.lv_health(atts[8])
        if attribute:
            attributes.append(attribute)
        if atts[9] == 'k':
            attribute = 'skip activation'
        if attribute:
            attributes.append(attribute)
        return attributes

    def vg_attributes(self, atts):
        attributes = []
        attribute = self.vg_permissions(atts[0])
        if attribute:
            attributes.append(attribute)
        if atts[1] == 'z':
            attributes.append('resizable')
        if atts[2] == 'x':
            attributes.append('exported')
        if atts[3] == 'p':
            attributes.append('partial')
        attribute = self.vg_allocation_policy(atts[4])
        if attribute:
            attributes.append(attribute)
        attribute = self.vg_cluster(atts[5])
        if attribute:
            attributes.append(attribute)
        return attributes

    def vg_permissions(self, att):
        # 1  Permissions: (w)riteable, (r)ead-only
        return {'w': 'writeable',
                'r': 'read-only'}.get(att, None)

    def vg_allocation_policy(self, att):
        #  Allocation policy: (c)ontiguous, c(l)ing, (n)ormal, (a)nywhere
        return {'c': 'contiguous',
                'l': 'cling',
                'n': 'normal',
                'a': 'anywhere'}.get(att, None)

    def vg_cluster(self, att):
        # (c)lustered, (s)hared
        return {'c': 'clustered',
                's': 'shared'}.get(att, None)

    def lv_volume_type(self, att):
        # Volume type: (m)irrored, (M)irrored without initial sync, (o)rigin, (O)rigin with merging snapshot,
        # (r)aid, (R)aid without initial sync, (s)napshot, merging (S)napshot, (p)vmove, (v)irtual, mirror
        # or raid (i)mage, mirror or raid (I)mage out-of-sync, mirror (l)og device, under (c)onversion,
        # thin (V)olume, (t)hin pool, (T)hin pool data, raid or thin pool m(e)tadata
        return {'m': 'mirrored',
                'M': 'mirrored without initial sync',
                'o': 'origin',
                'O': 'origin with merging snapshot',
                'r': 'raid',
                'R': 'raid without initial sync',
                's': 'snapshot',
                'S': 'merging snapshot',
                'p': 'pvmove',
                'v': 'virtual',
                'i': 'mirror or raid image',
                'I': 'image out of sync',
                'l': 'mirror log device',
                'c': 'under conversion',
                'V': 'thin volume',
                't': 'thin pool',
                'T': 'thin pool data',
                'e': 'raid or thin pool metadata'}.get(att, None)

    def lv_permissions(self, att):
        # Permissions: (w)riteable, (r)ead-only, (R)ead-only activation of non-read-only volume
        return {'w': 'writeable',
                'r': 'read-only',
                'R': 'read-only activation of non-read-only volume'}.get(att, None)

    def lv_allocation_policy(self, att):
        # Allocation policy: (a)nywhere, (c)ontiguous, (i)nherited, c(l)ing, (n)ormal
        return {'a': 'anywhere',
                'c': 'contiguous',
                'i': 'inherited',
                'l': 'cling',
                'n': 'normal',
                'A': 'anywhere (Locked)',
                'C': 'contiguous (Locked)',
                'I': 'inherited (Locked)',
                'L': 'cling (Locked)',
                'N': 'normal (Locked)'}.get(att, None)

    def lv_state(self, att):
        # State: (a)ctive, (s)uspended, (I)nvalid snapshot, invalid (S)uspended snapshot,
        # snapshot (m)erge failed, suspended snapshot (M)erge failed,
        # mapped (d)evice present without tables, mapped device present with (i)nactive table
        return {'a': 'active',
                's': 'suspended',
                'I': 'invalid snapshot',
                'S': 'invalid suspended snapshot',
                'm': 'snapshot merge failed',
                'M': 'suspended snapshot merge failed',
                'd': 'mapped device present without tables',
                'i': 'mapped device present with inactive table'}.get(att, None)

    def lv_device(self, att):
        # device (o)pen, (X) unknown
        return {'o': 'open',
                'X': 'unknown'}.get(att, None)

    def lv_target_type(self, att):
        # Target  type: (C)ache, (m)irror, (r)aid, (s)napshot, (t)hin, (u)nknown, (v)irtual
        return {'C': 'cache',
                'm': 'mirror',
                'r': 'raid',
                's': 'snapshot',
                't': 'thin',
                'u': 'unknown',
                'v': 'virtual'}.get(att, None)

    def lv_health(self, att):
        # Volume Health: (p)artial, (r)efresh needed, (m)ismatches exist, (w)ritemostly, (X) unknown
        return {'p': 'partial',
                'r': 'refresh needed',
                'm': 'mismatches exist',
                'w': 'writemostly',
                'X': 'unknown'}.get(att, None)
