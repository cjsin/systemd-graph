# System imports
import sys
import os
import re
from pprint import pprint,pformat
from collections import OrderedDict
from attrdict import AttrDict
import traceback

# Local imports
import util
from util import capture, verb, ep, verbose, Named
from graph import *
from formatters import *
from filters import *
#Node, Label, Edge, Graph, CycleDetection, Visitor, GraphAnalyzer, GraphFilter, CycleFilter, RimFilter, SinkFilter, SourceFilter, LeafFilter, GVFormatter

class Unit(Node):
    AFTER="After"
    BEFORE="Before"
    REQUIRES="Requires"
    WANTEDBY="WantedBy"
    WANTS="Wants"
    MOUNTS="RequiresMountsFor"
    DEVICE="device"
    TARGET="target"
    SLICE="slice"
    PATH="path"
    MOUNT="mount"
    SERVICE="service"
    SOCKET="socket"
    SWAP="swap"
    SCOPE="scope"
    TIMER="timer"
    AUTOMOUNT="automount"
    RELATIONSHIPS = [AFTER,BEFORE,REQUIRES,WANTEDBY,MOUNTS,WANTS]
    ALL_RELATIONSHIPS = RELATIONSHIPS
    ORDER_RELATIONSHIPS = [AFTER, BEFORE ]
    REQUIRES_RELATIONSHIPS = [REQUIRES, MOUNTS]
    HINT_RELATIONSHIPS = [WANTS, WANTEDBY]
    SOLID_RELATIONSHIPS = [AFTER,BEFORE,REQUIRES,MOUNTS]
    SHAPES={
        TARGET: "doubleoctagon",
        SOCKET: "insulator",
        PATH: "cds",
        DEVICE: "pentagon",
        SLICE: "assembly",
        MOUNT: "folder",
        SERVICE: "egg",
        TIMER: "star",
        SWAP: "noverhang",
        SCOPE: "component",
        AUTOMOUNT: "tab"
    }
    def __init__(self, name):
        super().__init__(name)
        self.load = ""
        self.active = ""
        self.sub = ""
        self.descr = ""
        self.relationships=OrderedDict()
        self.loaded=False
        for kind in Unit.RELATIONSHIPS:
            self.relationships[kind]=set()

    def id(self):
        return self.token

    def __str__(self):
        return self.token

    def _relationships(self, kind):
        return self.relationships[kind]

    def add_relationship(self, kind, other):
        flip = kind in [Unit.BEFORE]
        if flip:
            e = other._edge(self)
        else:
            e = self._edge(other)
        eid = e.id()
        label = e.incr(kind)
        #if flip:
        #    other._relationships(kind).add(e)
        #else:
        self._relationships(kind).add(e)
        return label

    def _token(self):
        t = self.name
        t = re.sub('\\\\x2d','-', t)
        t = re.sub("^-[.]","DASH.", t)
        t = re.sub("^[.]","DOT.", t)
        t = t.replace(":","--")
        t = re.sub("[.]mount$","_m", t)
        t = re.sub("[.]service$","_se", t)
        t = re.sub("[.]socket$","_so", t)
        t = re.sub("[.]scope$","_sc", t)
        t = re.sub("[.]slice$","_sl", t)
        t = re.sub("[.]path$","_p", t)
        t = re.sub("[.]device$","_d", t)
        t = re.sub("[.]target$","_ta", t)
        t = re.sub("[.]timer$","_ti", t)
        t = re.sub("[.]swap$","_sw", t)
        t = re.sub("[.]automount$","_am", t)
        return t

    def Relationship(self,kind):
        return list(self._relationships(kind).values())
