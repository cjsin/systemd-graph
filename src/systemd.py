import sys
import os
import re
from collections import OrderedDict
import util
from util import capture, verb, ep, verbose, Named
from pprint import pprint,pformat
from graph import *
from formatters import *
import traceback
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

    def id(self) -> str:
        return self.token

    def __str__(self) -> str:
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

    def _token(self) -> str:
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

class SystemdGVFormatter(GVFormatter):
    def stylise_node(self,n):
        ret={}
        ret.update(self.default_style)
        n = n.name
        what=n.split('.')[-1]

        if what in Unit.SHAPES:
            ret['shape']=Unit.SHAPES[what]
        return ret
    # def edge_labels(self, e) -> str:
    #     shorts=[]
    #     for x in e.Labels():
    #         t=x.name
    #         if t == Unit.MOUNTS:
    #             t="M"
    #         else:
    #             t=t[0]
    #         #c=x.count
    #         #if c > 1:
    #         #    t += "="+str(c)
    #         shorts.append(t)
    #     return "|".join(shorts)

class Systemd:
    COMMON=["--no-legend","--no-pager","--full"]
    LIST_UNITS=["systemctl","list-units","--plain","--all"]+COMMON
    SHOW_PROPERTY=["systemctl","show","--value"]+COMMON+["--property"]
    def __init__(self, defer=True, processing=None):
        self.units=OrderedDict()
        self.deferred=set()
        self.processing=processing or Unit.ALL_RELATIONSHIPS
        self.LoadUnits(defer=defer)

    def LoadUnits(self, defer=True,notfound=False,inactive=False,dead=False,exited=True):
        data = capture(Systemd.LIST_UNITS)
        for l in data:
            name, load, active, sub, *descr = l.split(None,5)
            verb(f"Generate unit {name}")
            if not notfound and load == 'not-found':
                ep(f"Skip not-found {name}")
                continue
            elif not inactive and active == 'inactive':
                ep(f"Skip inactive {name}")
                continue
            elif not dead and sub == 'dead':
                ep(f"Skip dead {name}")
                continue
            elif not exited and sub == 'exited':
                ep(f"Skip exited {name}")
                continue
            verb(2,f"Generate unit '{name}'")
            u = self._unit(name)
            u.load = load
            u.active = active
            u.sub = sub
            u.descr = descr
            if not defer:
                self.Unit(name)

    def Units(self):
        return list(self.units.values())

    def _unit(self, name) -> Unit:
        if name in self.units:
            return self.units[name]
        else:
            u = Unit(name)
            self.units[name]=u
            #print("Loading of " + name+ " is being deferred")
            self.deferred.add(name)
            return u

    def Unit(self,name) -> Unit:
        u = self._unit(name)
        if name in self.deferred or not u.loaded:
            ep(f"\rLoading deferred unit {name} \x1b[K")
            self._load_unit(u)
        return u

    def _load_unit(self, u):
        verb(2,"Loading data for unit " + str(u))
        name = u.name
        #print("Load "+name)
        if name not in self.deferred:
            #print("Already loaded")
            return u
        lazy = set()
        escaped_name = ['--', name ] if name.startswith('-') else [name]
        verb(2,"Escaped name for '{}' is {}".format(str(u),pformat(escaped_name)))
        for kind in self.processing:
            flip = kind in [Unit.AFTER, Unit.REQUIRES]
            verb(3,"Processing relationship "+kind)
            result = capture(Systemd.SHOW_PROPERTY+[kind]+escaped_name)
            if result:
                other_names = result[0].strip().split(' ')
                for other in other_names:
                    if not other:
                        continue
                    if kind == Unit.MOUNTS:
                        other='GEN-'+other.lstrip('/').replace('/','-') + '.mount'
                        #ep("Mapping RequiresMountsFor to new mount unit " + other)
                    ou = self._unit(other)
                    lazy.add(ou)
                    u.add_relationship(kind, ou)
            else:
                #print(f"No {kind} for {name}")
                pass
        u.loaded=True
        self.deferred.remove(name)
        for z in lazy:
            self._load_unit(z)
        return u

    def dump(self):
        units = self.Units()
        nunits = len(units)

        ep(f"{nunits} units to process.")
        if verbose() > 1:
            for n in range(0,len(units)):
                ep(f"{n}={units[n].name}")

        for n in range(0,len(units)):
            if n % 10 == 0:
                ep(f"\r{n}/{nunits} processed...\x1b[K")
            self.Unit(units[n].name)

        ep("\rAll units processed.")

        for u in units:
            ep(u)
            for e in u.Edges():
                ep(e)

    def Graph(self, name):
        if name is None:
            name="systemd"
        g = Graph(name)
        # First preprocess the units to pre-load and generate extras if required
        for u in self.Units():
            u = self.Unit(u.name)
        for u in self.Units():
            u = self.Unit(u.name)
            g.add_node(u)
            for e in u.Edges():
                g.add_edge(e)
        return g


PRUNE=[
    "^GEN-.*",
    "^user-.*",
    "[.]scope$",
    "[.]slice$",
    "[.]timer$",
    "[.]swap$",
    #"[.]socket$",
    "[.]device$",
    "^dev-",
    "^run-.*",
    "^user@",
    "^proc-",
    "dev-disk.*",
    "emergency.target",
    "rescue.target"
]

def main():
    try:
        util.check_environ()
        s = Systemd(processing=Unit.REQUIRES_RELATIONSHIPS)
        g = s.Graph("test")
        result = g
        changes=0
        result, changes2 = NodeNameFilter(PRUNE).filter(result)
        changes+=changes2
        #result, changes2 = CycleFilter().filter(result)
        #changes+=changes2
        result, changes2 = RepeatFilter(LeafFilter(),-6).filter(result)
        changes+=changes2
        #result, changes2 = RimFilter().filter(result)
        #changes+=changes2
        formatter = SystemdGVFormatter()
        dot_lines = formatter.graph(result)
        print_lines(dot_lines)
    except:
        traceback.print_exc()
if __name__ == "__main__":
    main()


