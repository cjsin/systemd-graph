import sys
import os
import re
from collections import OrderedDict
import util
from util import capture, verb, verb2, ep, verbose, Named
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
    SHAPES={
            Unit.TARGET: "doubleoctagon",
            Unit.SOCKET: "insulator",
            Unit.PATH: "cds",
            Unit.DEVICE: "pentagon",
            Unit.SLICE: "assembly",
            Unit.MOUNT: "folder",
            Unit.SERVICE: "egg",
            Unit.TIMER: "star",
            Unit.SWAP: "noverhang",
            Unit.SCOPE: "component",
            Unit.AUTOMOUNT: "tab"
        }
    def stylise_node(self,n):
        ret={}
        ret.update(self.default_style)
        n = n.name
        what=n.split('.')[-1]

        if what in SystemdGVFormatter.SHAPES:
            ret['shape']=SystemdGVFormatter.SHAPES[what]
        return ret
    def edge_labels(self, e):
        shorts=[]
        for x in e.Labels():
            t=x.name
            if t == Unit.MOUNTS:
                t="M"
            else:
                t=t[0]
            #c=x.count
            #if c > 1:
            #    t += "="+str(c)
            shorts.append(t)
        return "|".join(shorts)

class Systemd:
    def __init__(self, defer=True, processing=None, backend=None):
        self.units=OrderedDict()
        self.deferred=set()
        self.processing=processing or Unit.ALL_RELATIONSHIPS
        self.backend = backend if backend else CacheBackend(backend=LiveBackend())
        self.defer=defer
        self.LoadUnits()
        self.FinishLoading()
        self.backend.save()

    def LoadUnits(self):
        """ Perform an initial load of available units. FUrther info may be deferred."""
        units = self.backend.load_units()
        for name, udata in units.items():
            descr = udata['descr']
            descr = ' '.join(descr).strip()
            #verb2(f"Generate unit '{name}'")
            u = self._unit(name)
            u.status.extend([udata['load'], udata['active'], udata['sub']])
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

    def search(self, kinds, prune=None):
        for u in self.Units():
            u = self.Unit(u.name)

        all_set=False
        statuses=set()
        name_matchers=[]
        for k in kinds:
            if k == 'all':
                all_set = True
            elif k in Unit.STATUS:
                statuses.add(k)
            else:
                name_matchers.append(k)

        startwith=set()
        if all_set:
            verb("All units selected as a starting point")
            for u in self.Units():
                startwith.add(u.name)
        else:
            for u in self.Units():
                for nm in name_matchers:
                    if re.search(nm,u.name):
                        startwith.add(u.name)
                        break
        verb2("Starting with a set of units:"+pformat(startwith))
        if statuses:
            filterout = set()
            verb("Excluding units that do not match statuses " + pformat(statuses))
            for u in self.Units():
                if not u.status_match(statuses):
                    filterout.add(u.name)
            startwith = startwith - filterout

        if prune:
            filterout = set()
            verb("Excluding units that do not match names " + pformat(prune))
            for u in self.Units():
                for nm in prune:
                    if re.search(nm,u.name):
                        filterout.add(u.name)
                        break
            startwith = startwith - filterout

        return [self.Unit(x) for x in startwith]

    def Graph(self, name, backwards=True, units=None):
        if name is None:
            name="systemd"

        g = Graph(name)
        ep("Generating graph for " + str(len(units)) + " selected units")
        # First preprocess the units to pre-load and generate extras if required

        if units is None:
            units = self.Units()

        todo = set()
        done = set()
        for u in units:
            u = self.Unit(u.name)
            todo.add(u.name)

        # It is simple to go forwards, just follow the edges
        if not backwards:
            while len(todo):
                #ep("TODO: "+str(len(todo)))
                uname = todo.pop()
                if uname in done:
                    #ep("Aldready done")
                    continue

                u = self.Unit(uname)
                #ep("Add node " + u.name + " with " + str(len(u.Edges())) + " edges")
                g.add_node(u)
                done.add(uname)

                for e in u.Edges():
                    #ep("Check edge " + str(e))
                    a = e.a
                    b = e.b
                    if e.a.name not in done:
                        todo.add(e.a.name)

                    if e.b.name not in done:
                        todo.add(e.b.name)
                    #ep("Add edge " + str(e))
                    g.add_edge(e)

        else:
            #ep("Search network for forward links to these nodes")
            # we are going backwards, need to search the entire set of nodes
            # for forward edges that point to these nodes.
            while len(todo):
                verb("TODO: "+str(len(todo)))
                uname = todo.pop()
                if uname in done:
                    continue
                u = self.Unit(uname)
                g.add_node(u)
                done.add(uname)
                for u2 in self.Units():
                    verb("Search for units with edges going to " + uname)
                    if u2.name == uname:
                        continue
                    elif u2.name in done:
                        continue
                    elif u2.name in todo:
                        # do it later
                        continue
                    else:
                        for e in u2.Edges():
                            b = e.b
                            if b.name == uname:
                                aname = e.a.name
                                if aname not in todo and aname not in done:
                                    g.add_node(self.Unit(aname))
                                    g.add_edge(e)
                                    #ep("Add edge " + str(e))
                                    todo.add(aname)

            # Now we will have all interesting nodes in 'done'
        return g


