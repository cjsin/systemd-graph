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
from attrdict import AttrDict
#Node, Label, Edge, Graph, CycleDetection, Visitor, GraphAnalyzer, GraphFilter, CycleFilter, RimFilter, SinkFilter, SourceFilter, LeafFilter, GVFormatter
import traceback
from backend import *
from unit import Unit

class SystemdGVFormatter(GVFormatter):
    def stylise_node(self,n):
        ret={}
        ret.update(self.default_style)
        n = n.name
        what=n.split('.')[-1]

        if what in Unit.SHAPES:
            ret['shape']=Unit.SHAPES[what]
        return ret
    # def edge_labels(self, e):
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
    def __init__(self, defer=True, processing=None, backend=None, notfound=False, inactive=False, dead=False, exited=True):
        self.units=OrderedDict()
        self.deferred=set()
        self.processing=processing or Unit.ALL_RELATIONSHIPS
        self.backend = backend if backend else CacheBackend(backend=LiveBackend())
        self.defer=defer
        self.notfound = notfound
        self.inactive  = inactive
        self.dead = dead
        self.exited = exited
        self.LoadUnits()
        self.FinishLoading()
        self.backend.save()

    def LoadUnits(self):
        """ Perform an initial load of available units. FUrther info may be deferred."""
        units = self.backend.load_units()
        for name, udata in units.items():
            #verb(f"Generate unit {name}")
            if not self.notfound and udata['load'] == 'not-found':
                #verb1(f"Skip not-found {name}")
                continue
            elif not self.inactive and udata['active'] == 'inactive':
                #verb1(f"Skip inactive {name}")
                continue
            elif not self.dead and udata['sub'] == 'dead':
                #verb1(f"Skip dead {name}")
                continue
            elif not self.exited and udata['sub'] == 'exited':
                #verb1(f"Skip exited {name}")
                continue
            #verb2(f"Generate unit '{name}'")
            u = self._unit(name)
            u.load = udata['load']
            u.active = udata['active']
            u.sub = udata['sub']
            u.descr = udata['descr']
            u.loaded = False
            #u.update(udata)
            if not self.defer:
                self.Unit(name)

    def FinishLoading(self):
        ep("")
        for u in self.Units():
            self.Unit(u.name)
        ep("")

    def Units(self):
        return list(self.units.values())

    def _unit(self, name):
        if name in self.units:
            return self.units[name]
        else:
            u = Unit(name)
            self.units[name]=u
            #print("Loading of " + name+ " is being deferred")
            self.deferred.add(name)
            return u

    def Unit(self,name):
        u = self._unit(name)
        if name in self.deferred or not u.loaded:
            #ep(f"\rLoading deferred unit {name} \x1b[K")
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
        for kind in self.processing:
            flip = kind in [Unit.AFTER, Unit.REQUIRES]
            #ep("Processing relationship "+kind)

            other_names = self.backend.unit_property(name, kind) or []
            for other in other_names:
                if not other:
                    continue
                if kind == Unit.MOUNTS:
                    other='GEN-'+other.lstrip('/').replace('/','-') + '.mount'
                    #ep("Mapping RequiresMountsFor to new mount unit " + other)
                ou = self._unit(other)
                lazy.add(ou)
                u.add_relationship(kind, ou)
        u.loaded = True
        self.deferred.remove(name)
        for z in lazy:
            self._load_unit(z)
        return u

    def dump(self):
        units = self.Units()
        nunits = len(units)

        #ep(f"{nunits} units to process.")
        if verbose() > 1:
            for n in range(0,len(units)):
                #ep(f"{n}={units[n].name}")
                pass

        for n in range(0,len(units)):
            if n % 10 == 0:
                #ep(f"\r{n}/{nunits} processed...\x1b[K")
                pass
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

