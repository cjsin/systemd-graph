from __future__ import annotations # Allow type hints without forward declarations
import pytest
from util import ep
from pprint import pformat
from graph import *

from testutil import load_graph, dump_graph

class UppercaseNode(Node):
    def _token(self) -> str:
        return self.name.upper()

def test_repr():
    a = Node("a")
    b = Node("b")
    assert len(repr(a)) > 0
    e = Edge(a,b)
    erepr = repr(e)
    assert len(erepr) > 0
    lab = e.incr("data")
    assert len(repr(lab)) > 0
    assert len(repr(e)) >len(erepr)

    g1 = Graph("name")
    g1.add_edge(e)
    g2 = Graph("name")
    g2.add_node(a)
    g2.add_node(b)
    g2.add_edge(e)
    assert len(repr(g1)) == len(repr(g2))
    assert repr(g1) == repr(g2)

def test_label_incr():
    l = Label("a")
    assert l.count == 0
    assert l.incr() == 1
    assert l.incr() == 2
    assert l.incr() == 3
    l = Label("b")
    assert l.count == 0
    assert l.incr() == 1

def test_label_count():
    assert Label("a").count == 0

def test_label_id():
    assert Label("a").id() == "a"

def test_node_token():
    assert Node("a").token == "a"
    assert Node("xyz-abc").token == "xyz-abc"
    assert UppercaseNode("lower").token == "LOWER"

def test_node_id():
    assert Node("a").id() == "a"
    assert UppercaseNode("lower").id() == "LOWER"

def test_node_add_edge():
    a = Node("a")
    b = Node("b")
    e = a.add_edge(b)
    assert e.a == a
    assert e.b == b
    assert len(a.Edges()) == 1
    assert a.Edges()[0] == e

def test_edge_id():
    a = Node("a")
    b = Node("b")
    e = Edge(a,b)
    assert e.id().replace(' ','') == "a->b"

def test_edge_labels():
    a = Node("a")
    b = Node("b")
    e = Edge(a,b)
    assert len(e.Labels()) == 0

    e.add_label("label1")
    assert len(e.Labels()) == 1

    e.add_label("duplicate")
    assert len(e.Labels()) == 2
    assert e.incr("duplicate").count == 1

    assert e.add_label("duplicate").count == 1
    assert len(e.Labels()) == 2
    assert e.incr("duplicate").count == 2

    assert e.incr("label1").count == 1
    assert e.incr("label1").count == 2

def test_graph_counts():
    g = load_graph("test",{})
    assert g.edgecount() == 0
    assert g.nodecount() == 0
    g = load_graph("test",{'c-a':'ca','c-b':'cb','c-d':'cd','c-e':'ce'})
    assert g.edgecount() == 4
    assert g.nodecount() == 5
    g = load_graph("test",{'c-a':'ca','c-b':'cb','b-c':'bc','b-d':'bd'})
    assert g.edgecount() == 4
    assert g.nodecount() == 4

def test_graph_shallow_copy():
    g = load_graph("test",{'c-a':'ca','c-b':'cb','b-c':'bc','b-d':'bd'})
    g2 = g.shallow_copy()
    assert g.edgecount() == g2.edgecount()
    assert g.nodecount() == g.nodecount()

def test_graph_add_graph():
    a = load_graph("test",{'c-a':'ca','c-b':'cb'})
    b = load_graph("test",{'d-e':'de','e-f':'ef','f-g':'fg'})
    c = load_graph("test",{'c-a':'ca','c-b':'cb','d-e':'de','e-f':'ef','f-g':'fg'})
    assert a.nodecount()+b.nodecount() == c.nodecount()
    assert a.edgecount()+b.edgecount() == c.edgecount()

def test_graph_add_node():
    g = load_graph("test",{'c-a':'ca','c-b':'cb'})
    n = Node("n")
    n2 = g.add_node(n)
    assert g.node("n") == n
    assert n2 == n

def test_graph_edge():
    g = Graph("g")
    a = Node("a")
    b = Node("b")
    e = a.add_edge(b)
    g.add_edge(e)
    assert g.edge(e.key()) == e
    assert g.edge("a->other") == None
    assert g.nodecount() == 2

def test_graph_nodes():
    g = Graph("g")
    a = Node("a")
    b = Node("b")
    e = a.add_edge(b)
    g.add_edge(e)
    assert len(g.nodes()) == 2
    assert a in g.nodes()
    assert b in g.nodes()

def test_graph_edges():
    g = Graph("g")
    a = Node("a")
    b = Node("b")
    e = a.add_edge(b)
    g.add_edge(e)
    assert len(g.edges()) == 1
    assert e in g.edges()

def test_graph_node():
    g = Graph("g")
    a = Node("a")
    g.add_node(a)
    assert g.nodecount() == 1
    b = Node("b")
    g.add_node(b)
    assert g.nodecount() == 2
    g.add_node(b)
    assert g.nodecount() == 2

def test_graph_add_edge():
    g = Graph("g")
    a = Node("a")
    b = Node("b")
    e = a.add_edge(b)
    e2 = g.add_edge(e)
    assert e == e2
    assert g.edgecount() == 1
    assert g.nodecount() == 2


def test_alternate_build_methods():
    compare_alternate_build_methods({'c-a':'ca'})
    compare_alternate_build_methods({'c-a':'ca','c-b':'cb'})
    compare_alternate_build_methods({'c-a':'ca','c-b':'cb','d-e':'de'})
    compare_alternate_build_methods({'c-a':'ca','c-b':'cb','d-e':'de','e-f':'ef'})
    compare_alternate_build_methods({'c-a':'ca','c-b':'cb','d-e':'de','e-f':'ef','f-g':'fg'})

def compare_alternate_build_methods(test_data):
    ga = alternate_build_method_1(test_data)
    gb = alternate_build_method_2(test_data)
    assert ga.nodecount() == gb.nodecount()
    assert ga.edgecount() == gb.edgecount()
    assert ",".join([str(x) for x in ga.nodes()]) == ",".join([str(x) for x in gb.nodes()])
    assert ",".join([str(x) for x in gb.edges()]) == ",".join([str(x) for x in gb.edges()])
    assert repr(ga) == repr(gb)

def dump(g):
    ep(f"Graph {g} :")
    dump_graph(g)
    ep(repr(g))

def alternate_build_method_1(test_data):
    g = Graph("g")
    for edgespec,label in test_data.items():
        a,b = edgespec.split('-')
        a = g.add_node(Node(a))
        b = g.add_node(Node(b))
        e = g.add_edge(a.add_edge(b))
        e.add_label(label)
    return g

def alternate_build_method_2(test_data):
    g = Graph("g")
    for edgespec,label in test_data.items():
        a,b = edgespec.split('-')
        a = Node(a)
        b = Node(b)
        e = g.add_edge(a.add_edge(b))
        e.add_label(label)
    return g
