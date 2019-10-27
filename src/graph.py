from __future__ import annotations # Allow type hints without forward declarations

import traceback
from collections import OrderedDict, Counter
from util import Named
from typing import List, Set, Dict, Tuple, Optional
StrList=List[str]
from util import *
from pprint import pformat
import re
import logging

log = logging.getLogger(__name__)

class Label(Named):
    count: int

    def __init__(self, name: str):
        super().__init__(name)
        self.count=0

    def incr(self) -> int:
        self.count+=1
        return self.count

    def id(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name+('' if self.count==1 else "="+str(self.count))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}={self.count})"

LabelList=List[Label]

class Node(Named):
    token: str
    _edges: OrderedDict

    def __init__(self, name: str):
        super().__init__(name)
        self.token = self._token()
        # Note that we cannot initialise _edges  etc with an object
        # because then it would be shared between all instances!
        # So the type hint is useful only for basic types (int, etc) and typing
        self._edges=OrderedDict()
        verb("Create node({id(self)}={name})")
    def __repr__(self):
        edgestr = ",".join([repr(x) for x in self._edges.values()])
        return f"{self.__class__.__name__}.{self.name}(id={self.token},edges={edgestr})"

    def _token(self) -> str:
        return self.name

    def id(self) -> str:
        return self.token

    def add_edge(self, other: Node):
        return self._edge(other)

    # TODO - rework so edges are a property of the graph, not the nodes
    def _edge(self, other: Node):
        e = Edge(self, other)
        ekey = e.key()
        if ekey in self._edges:
            return self._edges[ekey]
        else:
            self._edges[ekey] = e
            return e

    def edges(self) -> EdgeList:
        return list(self._edges.values())

    # TODO: deprecate and remove uses of this
    def Edges(self) -> EdgeList:
        return self.edges()

NodeList=List[Node]

class Edge(Named):
    a: Node
    b: Node
    _labels: OrderedDict

    def __init__(self,a,b, *labels):
        assert a is not None
        assert b is not None
        super().__init__("{} -> {}".format(a.token, b.token))
        self.a : Node =a
        self.b : Node =b
        self._labels = OrderedDict()

        if labels:
            for label_name, label in labels:
                self._labels[label_name] = label

    def id(self):
        return self.name

    def key(self) -> str:
        return f"{id(self.a)}.{id(self.b)}"

    # TODO: deprecate and remove uses of this
    def Labels(self) -> LabelList:
        return self.labels()

    def labels(self) -> LabelList:
        return list(self._labels.values())

    def add_label(self, labeltext: str):
        """ Add a label. Adding an existing label does not increment its count, it must be explicitly incremented"""
        return self._label(labeltext)

    def _label(self, labeltext: str) -> Label:
        l = None
        if labeltext in self._labels:
            l = self._labels[labeltext]
        else:
            l = Label(labeltext)
            self._labels[labeltext]=l
        return l

    def incr(self,labeltext : str) -> Label:
        l = self._label(labeltext)
        if l:
            verb(f"Incrementing label {labeltext}")
            l.incr()
        return l

    def __str__(self) -> str:
        return '{}->{}[{}]'.format(self.a.token,self.b.token, '|'.join([str(x) for x in self._labels.keys()]))

    def __repr__(self) -> str:
        labelstr = '|'.join([repr(x) for x in self._labels.values()])
        return '{}(a={},b={},labels={})'.format(self.__class__.__name__, self.a.token, self.b.token, labelstr)

EdgeList=List[Edge]

class Graph(Named):

    def __init__(self, name: str):
        super().__init__(name)
        self._edges={}
        self._nodes={}

    def nodecount(self) -> int:
        return len(self._nodes.keys())

    def edgecount(self) -> int:
        return len(self._edges.keys())

    def shallow_copy(self) -> Graph:
        g = Graph(self.name)
        self._add(g)
        return g

    def add(self, other: Graph) -> Graph:
        other._add(self)
        return self

    def _add(self, addto: Graph) -> Graph:
        if addto == self:
            return
        for n in self.nodes():
            addto.add_node(n)
        for e in self.edges():
            addto.add_edge(e)
        return addto

    def add_node(self, n: Node) -> Node:
        nid = n.id()
        if nid in self._nodes:
            if n != self._nodes[nid]:
                n2 = n
                n1 = self._nodes[nid]
                r1 = repr(n1)
                r2 = repr(n2)
                i1 = id(n1)
                i2 = id(n2)
                ep(f"Warning: replacing node {r1} with another that has the same name: {r2}.")
                ep(f"Two nodes are {i1}({n1}) and {i2}({n2})")
        self._nodes[n.id()]=n
        return n

    def add_edge(self, e: Edge) -> Edge:
        if e is None:
            return None

        eid = e.id()
        ekey = e.key()
        if ekey in self._edges:
            if e != self._edges[eid]:
                r1 = repr(self._edges[eid])
                r2 = repr(e)
                ep(f"Warning: replacing edge {r1} with another that has the same name: {r2}.")
        else:
            for e2 in self._edges.values():
                e2id = e2.id()
                if e2id == eid:
                    r1 = repr(self._edges[eid])
                    r2 = repr(e)
                    ep(f"Warning: adding another edge {r2} with same node names but different nodes than existing {r1}")
        self._edges[e.key()]=e
        a = e.a
        if a.id() not in self._nodes:
            verb2(f"Warning: Node {a.id()} is not yet contained within the graph - adding it.")
            self.add_node(a)
        b = e.b
        if b.id() not in self._nodes:
            verb2(f"Node {b.id()} is not yet contained within the graph - adding it.")
            self.add_node(b)
        return e

    def nodes(self) -> NodeList:
        return list(self._nodes.values())

    def edges(self) -> EdgeList:
        return list(self._edges.values())

    def node(self,nid: str) -> Node:
        return self._nodes.get(nid,None)

    def edge(self, ekey: str) -> Node:
        return self._edges.get(ekey,None)

    def __repr__(self) -> str:
        out = []
        out.append(self.__class__.__name__+"(")
        e = self.edges()
        n = self.nodes()
        n=",".join(sorted([str(x) for x in n]))
        e=",".join(sorted([str(x) for x in e]))
        out.append(f"n={n},e={e}")
        out.append(")")
        return "".join(out)

    def check(self, allow_islands=False) -> bool:
        # check that all nodes from edges are part of
        # the graph.
        seen_nids=Counter()
        seen_nodes=set()
        ret=[]
        for e in self._edges.values():
            aid=e.a.id()
            bid=e.b.id()
            if aid not in self._nodes:
                ret.append(f"ID {aid} seen in edges but not nodes")
            if bid not in self._nodes:
                ret.append(f"ID {bid} seen in edges but not nodes")
            if e.a not in self._nodes.values():
                ret.append(f"node {e.a} seen in edges but not nodes")
            if e.b not in self._nodes.values():
                ret.append(f"node {e.b} seen in edges but not nodes")
            if self.node(aid) != e.a:
                ret.append(f"edge node {aid} = {e.a} does not match the graph node with that id: {self.node(aid)}")
                ret.append(f"edge a id() == {id(e.a)} while graph a id() == {id(self.node(aid))}")
            if self.node(bid) != e.b:
                ret.append(f"edge node {bid} = {e.b} does not match the graph node with that id: {self.node(bid)}")
                ret.append(f"edge b id() == {id(e.b)} while graph b id() == {id(self.node(bid))}")
            seen_nids[aid]+=1
            seen_nids[bid]+=1
            seen_nodes.add(e.a)
            seen_nodes.add(e.b)

        for k in seen_nids.keys():
            if k not in self._nodes:
                ret.append(f"{k} seen in edges but not nodes")

        if not allow_islands:
            for nid,n in self._nodes.items():
                if nid not in seen_nids:
                    ret.append(f"node {nid} {n} was not present in any edges.")

        for n in seen_nodes:
            if n not in self._nodes.values():
                ret.append(f"Node from edge {n} was not present in nodes list.")

        if not ret:
            ep("No Issues were detected:")
        if ret:
            ep("Warning: Issues were detected with this graph:")
            print_lines(ret)

        return ret

GraphList=List[Graph]
