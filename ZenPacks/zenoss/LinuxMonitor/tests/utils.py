##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

# stdlib Imports
import functools
import re

# Zope Imports
from zope.component import subscribers

# Zenoss Imports
from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenUtils.guid.interfaces import IGUIDManager

# DynamicView Imports
try:
    from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS
    from ZenPacks.zenoss.DynamicView.interfaces import IRelatable
except ImportError:
    TAG_IMPACTED_BY, TAG_IMPACTS, IRelatable = None, None, None

# Impact Imports
try:
    from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider
except ImportError:
    IRelationshipDataProvider = None


def create_device(dmd, zPythonClass, device_id, datamaps):
    device = dmd.Devices.findDeviceByIdExact(device_id)
    if not device:
        deviceclass = dmd.Devices.createOrganizer("/Server/SSH/Linux")
        deviceclass.setZenProperty("zPythonClass", zPythonClass)
        device = deviceclass.createInstance(device_id)

    adm = ApplyDataMap()._applyDataMap

    [adm(device, datamap) for datamap in datamaps]

    return device


def id_from_path(path):
    return path.split("/")[-1]


def id_from_guid_fn(dmd):
    guid_manager = IGUIDManager(dmd)

    def id_from_guid(guid):
        return guid_manager.getObject(guid).id

    return id_from_guid


def triples_from_device(device, fn):
    return reduce(set.union, map(fn, [device] + device.getDeviceComponents()))


def dynamicview_triples_from_obj(obj, tags=None):
    if not tags:
        raise ValueError("tags must be a list of DynamicView relationship tags")

    relatable = IRelatable(obj)

    triples = set()
    for tag in tags:
        for relation in relatable.relations(type=tag):
            triples.add((
                id_from_path(relation.source.id),
                tag,
                id_from_path(relation.target.id)))

    return triples


def dynamicview_triples_from_device(device, tags=None):
    return triples_from_device(
        device,
        functools.partial(dynamicview_triples_from_obj, tags=tags))


def impact_triples_from_obj(obj):
    id_from_guid = id_from_guid_fn(obj.getDmd())

    triples = set()
    for subscriber in subscribers([obj], IRelationshipDataProvider):
        for edge in subscriber.getEdges():
            impacted_id = id_from_guid(edge.impacted)
            source_id = id_from_guid(edge.source)
            if source_id == obj.id:
                triples.add((obj.id, TAG_IMPACTS, impacted_id))
            elif impacted_id == obj.id:
                triples.add((obj.id, TAG_IMPACTED_BY, source_id))
            else:
                # No else. In practice we don't have an object's
                # IRelationshipDataProvider provide relationships that
                # don't have the object terminating one side of the
                # edge because it's too easy for the edge to not be
                # updated when the object is updated.
                pass

    return triples


def impact_triples_from_device(device):
    return triples_from_device(device, impact_triples_from_obj)


def triples_from_yuml(yuml):
    line_matcher = re.compile(
        r"^\s*"
        r"\[(?P<source>[^\]]+)\]"
        r"(?P<connector>[^\[]+)"
        r"\[(?P<target>[^\]]+)\]"
        r"\s*$").search

    triples = set()
    for line in yuml.strip().splitlines():
        line = line.strip()
        if line.startswith("//"):
            continue

        match = line_matcher(line)
        if match:
            source, connector, target = match.groups()
            if connector == "->":
                triples.add((source, TAG_IMPACTS, target))
            else:
                raise ValueError(
                    "{!r} unsupported connector in {!r}"
                    .format(connector, line))
        else:
            raise ValueError(
                "{!r} isn't a recognized YUML line"
                .format(line))

    return triples


def complement_triple(triple, tag_map=None):
    if tag_map is None:
        tag_map = {
            TAG_IMPACTS: TAG_IMPACTED_BY,
            TAG_IMPACTED_BY: TAG_IMPACTS,
            }

    source, tag, target = triple
    complemented_tag = tag_map.get(tag)
    if complemented_tag:
        return (target, complemented_tag, source)


def complement_triples(triples, tag_map=None):
    complemented_triples = set()
    for triple in triples:
        complemented_triples.add(triple)

        complemented_triple = complement_triple(triple, tag_map)
        if complemented_triple:
            complemented_triples.add(complemented_triple)

    return complemented_triples


def yuml_from_triples(triples, missing=None, extra=None, tag_map=None):
    missing = set() if missing is None else missing
    extra = set() if extra is None else extra

    def filter_triples(ts):
        if tag_map:
            return {t for t in ts if t[1] in tag_map}
        else:
            return ts

    def symbol_for_triple(triple):
        if triple in missing:
            return "XXX"
        elif triple in extra:
            return "!!!"
        else:
            return ""

    lines = []
    for triple in filter_triples(triples | extra):
        source, tag, target = triple

        left = symbol_for_triple(triple)

        if tag in tag_map:
            right = symbol_for_triple(complement_triple(triple))
        else:
            right = ""

        middle = "-.-" if any((left, right)) else "-"

        lines.append(
            "[{}]{}{}{}>[{}]".format(
                source, left, middle, right, target))

    return "\n".join(sorted(lines))


def impact_yuml_from_device(device):
    triples = impact_triples_from_device(device)
    complemented_triples = complement_triples(
        triples,
        tag_map={
            TAG_IMPACTS: TAG_IMPACTED_BY,
            TAG_IMPACTED_BY: TAG_IMPACTS,
            })

    return yuml_from_triples(
        triples,
        missing=complemented_triples - triples,
        tag_map={
            TAG_IMPACTS: TAG_IMPACTED_BY,
            })
