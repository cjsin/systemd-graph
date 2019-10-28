#from __future__ import annotations # Allow type hints without forward declarations

import traceback
from collections import OrderedDict, Counter
from util import Named
#from typing import List, Set, Dict, Tuple, Optional
#StrList=List[str]
from util import *
from pprint import pformat
import re
import logging

log = logging.getLogger(__name__)

class Label(Named):

    def __init__(self, name):
        super().__init__(name)
        self.count=0

    def incr(self):
        self.count+=1
        return self.count

    def id(self):
        return self.name

    def __str__(self):
        return self.name+('' if self.count==1 else "="+str(self.count))

    def __repr__(self):
        #return f"{self.__class__.__name__}({self.name}={self.count})"
        return "{}({}={})".format(self.__class__.__name__,self.name,self.count)

#LabelList=List[Label]

class Node(Named):

    def __init__(self, name):
        super().__init__(name)
        self.token = self._token()
        # Note that we cannot initialise _edges  etc with an object
        # because then it would be shared between all instances!
        # So the type hint is useful only for basic types (int, etc) and typing
        self._edges=OrderedDict()
        #verb("Create node({}={})".format(id(self),name))

    def __repr__(self):
        edgestr = ",".join([repr(x) for x in self._edges.values()])
        #return f"{self.__class__.__name__}.{self.name}(id={self.token},edges={edgestr})"
        return "{}.{}(id={},edges={})".format(self.__class__.__name__,self.name,self.token,edgestr)

    def _token(self):
        return self.name

    def id(self):
        return self.token

    def key(self):
        return id(self)

    def add_edge(self, other):
        return self._edge(other)

    # TODO - rework so edges are a property of the graph, not the nodes
    def _edge(self, other):
        e = Edge(self, other)
        ekey = e.key()
        if ekey in self._edges:
            return self._edges[ekey]
        else:
            self._edges[ekey] = e
            return e

    def edges(self):
        return list(self._edges.values())

    # TODO: deprecate and remove uses of this
    def Edges(self):
        return self.edges()

#NodeList=List[Node]

class Edge(Named):

    def __init__(self,a,b, *labels):
        assert a is not None
        assert b is not None
        super().__init__("{} -> {}".format(a.token, b.token))
        self.a =a
        self.b =b
        self._labels = OrderedDict()

        if labels:
            for label_name, label in labels:
                self._labels[label_name] = label

    def id(self):
        return self.name

    def key(self):
        #return f"{id(self.a)}.{id(self.b)}"
        return str(id(self.a))+"."+str(id(self.b))

    # TODO: deprecate and remove uses of this
    def Labels(self):
        return self.labels()

    def labels(self):
        return list(self._labels.values())

    def add_label(self, labeltext):
        """ Add a label. Adding an existing label does not increment its count, it must be explicitly incremented"""
        return self._label(labeltext)

    def _label(self, labeltext):
        l = None
        if labeltext in self._labels:
            l = self._labels[labeltext]
        else:
            l = Label(labeltext)
            self._labels[labeltext]=l
        return l

    def incr(self,labeltext):
        l = self._label(labeltext)
        if l:
            verb("Incrementing label "+labeltext)
            l.incr()
        return l

    def __str__(self):
        return '{}->{}[{}]'.format(self.a.token,self.b.token, '|'.join([str(x) for x in self._labels.keys()]))

    def __repr__(self):
        labelstr = '|'.join([repr(x) for x in self._labels.values()])
        return '{}(a={},b={},labels={})'.format(self.__class__.__name__, self.a.token, self.b.token, labelstr)


#EdgeList=List[Edge]

class Graph(Named):

    def __init__(self, name):
        super().__init__(name)
        self._edges={}
        self._nodes={}

    def nodecount(self):
        return len(self._nodes.keys())

    def edgecount(self):
        return len(self._edges.keys())

    def shallow_copy(self):
        g = Graph(self.name)
        self._add(g)
        return g

    def add(self, other):
        other._add(self)
        return self

    def _add(self, addto):
        if addto == self:
            return
        for n in self.nodes():
            addto.add_node(n)
        for e in self.edges():
            addto.add_edge(e)
        return addto

    def add_node(self, n):
        nid = n.id()
        if nid in self._nodes:
            if n != self._nodes[nid]:
                n2 = n
                n1 = self._nodes[nid]
                r1 = repr(n1)
                r2 = repr(n2)
                i1 = id(n1)
                i2 = id(n2)
                #ep(f"Warning: replacing node {r1} with another that has the same name: {r2}.")
                #ep(f"Two nodes are {i1}({n1}) and {i2}({n2})")
        self._nodes[n.id()]=n
        return n

    def add_edge(self, e):
        if e is None:
            return None

        eid = e.id()
        ekey = e.key()
        if ekey in self._edges:
            if e != self._edges[eid]:
                r1 = repr(self._edges[eid])
                r2 = repr(e)
                #ep(f"Warning: replacing edge {r1} with another that has the same name: {r2}.")
        else:
            for e2 in self._edges.values():
                e2id = e2.id()
                if e2id == eid:
                    r1 = repr(self._edges[eid])
                    r2 = repr(e)
                    #ep(f"Warning: adding another edge {r2} with same node names but different nodes than existing {r1}")
        self._edges[e.key()]=e
        a = e.a
        if a.id() not in self._nodes:
            verb2("Warning: Node {} is not yet contained within the graph - adding it.".format(a.id()))
            self.add_node(a)
        b = e.b
        if b.id() not in self._nodes:
            verb2("Node {} is not yet contained within the graph - adding it.".format(b.id()))
            self.add_node(b)
        return e

    def nodes(self):
        return list(self._nodes.values())

    def edges(self):
        return list(self._edges.values())

    def node(self,nid):
        return self._nodes.get(nid,None)

    def edge(self, ekey):
        return self._edges.get(ekey,None)

    def __repr__(self):
        out = []
        out.append(self.__class__.__name__+"(")
        e = self.edges()
        n = self.nodes()
        n=",".join(sorted([str(x) for x in n]))
        e=",".join(sorted([str(x) for x in e]))
        out.append("n={},e={}".format(n,e))
        out.append(")")
        return "".join(out)

    def check(self, allow_islands=False):
        # check that all nodes from edges are part of
        # the graph.
        seen_nids=Counter()
        seen_nodes=set()
        ret=[]
        for e in self._edges.values():
            aid=e.a.id()
            bid=e.b.id()
            # Can't do these until I rewrite them to not use f-strings (requires python 3.6 or higher)
            # if aid not in self._nodes:
            #     ret.append(f"ID {aid} seen in edges but not nodes")
            # if bid not in self._nodes:
            #     ret.append(f"ID {bid} seen in edges but not nodes")
            # if e.a not in self._nodes.values():
            #     ret.append(f"node {e.a} seen in edges but not nodes")
            # if e.b not in self._nodes.values():
            #     ret.append(f"node {e.b} seen in edges but not nodes")
            # if self.node(aid) != e.a:
            #     ret.append(f"edge node {aid} = {e.a} does not match the graph node with that id: {self.node(aid)}")
            #     ret.append(f"edge a id() == {id(e.a)} while graph a id() == {id(self.node(aid))}")
            # if self.node(bid) != e.b:
            #     ret.append(f"edge node {bid} = {e.b} does not match the graph node with that id: {self.node(bid)}")
            #     ret.append(f"edge b id() == {id(e.b)} while graph b id() == {id(self.node(bid))}")
            seen_nids[aid]+=1
            seen_nids[bid]+=1
            seen_nodes.add(e.a)
            seen_nodes.add(e.b)

        # for k in seen_nids.keys():
        #     if k not in self._nodes:
        #         ret.append(f"{k} seen in edges but not nodes")

        # if not allow_islands:
        #     for nid,n in self._nodes.items():
        #         if nid not in seen_nids:
        #             ret.append(f"node {nid} {n} was not present in any edges.")

        # for n in seen_nodes:
        #     if n not in self._nodes.values():
        #         ret.append(f"Node from edge {n} was not present in nodes list.")

        if not ret:
            ep("No Issues were detected:")
        if ret:
            ep("Warning: Issues were detected with this graph:")
            print_lines(ret)

        return ret

#GraphList=List[Graph]
