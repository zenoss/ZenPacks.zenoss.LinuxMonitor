##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
utility module for linux monitor

LVMAttributes is a class for parsing attributes from pvs,vgs,lvs
'''
import re


class LVMAttributeParser(object):

    def pv_attributes(self, atts):
        # (a)llocatable, e(x)ported and (m)issing
        attributes = []
        for i in range(len(atts)):
            if i == 0 and atts[0] == 'a':
                attributes.append('allocatable')
            if i == 1 and atts[1] == 'x':
                attributes.append('exported')
            if i == 2 and atts[2] == 'm':
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
        if len(atts) > 6:
            attribute = self.lv_target_type(atts[6])
            if attribute:
                attributes.append(attribute)
            if len(atts) > 8:
                attribute = self.lv_health(atts[8])
                if attribute:
                    attributes.append(attribute)
            if len(atts) > 9:
                if atts[9] == 'k':
                    attributes.append('skip activation')
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


# -----------------------------------------------------------------------------
# Global Utility Functions
# -----------------------------------------------------------------------------
def override_graph_labels(component, drange):
    # Return a list of modified graphs, given component and drange
    # Don't modify titles if graphs are already overidden

    graphs = []
    if not component:
        return graphs

    for g in component.getDefaultGraphDefs(drange):
        if not g.get('title_override'):

            title = "{} ({}: {})".format(
                g["title"],
                component.class_label,
                component.titleOrId()
                )

            # Reduce size of title so it fits on graph without pushing buttons
            uid_pattern_re = re.compile('([\w]{8})(--\w{4}){3}--\w{12}')
            title = uid_pattern_re.sub(r'\1', title)
            title = title.replace('cinder--volumes-_snapshot-', 'cinder-snap')

            g = {
                "title": title,
                "url": g["url"],
                "title_override": True,
                }

        graphs.append(g)

    return graphs
