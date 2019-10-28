import pytest

from visitor import Visitor
from graph import *
from util import verb
from attrdict import AttrDict
from pprint import pprint, pformat
from testutil import load_graph

def new_visitor(sorting=False, data=None, extra_data=None):
    if data is None:
        data = {'a-b':'ab','b-c':'bc'}
    g = load_graph('test-visitor',data)
    record=AttrDict()
    record.visited=[]
    record.origins={}

    def tf(d):
        return extra_data
    def vf(data, iteration, origin, steps):
        if data.nid in record.visited:
            verb("This node was already visited.")
            return False
        verb("This node not visited yet.")
        record.visited.append(data.nid)
        record.origins[data.nid]=origin
        return True
    v = Visitor(g, tf, vf, sorting=sorting)
    return v, g, record


def test_nodes():
    v, g, record = new_visitor(sorting=True,data={'c-a':'ca','c-b':'cb','b-c':'bc','b-d':'bd'})
    datas = v.Visit()
    nodes = v.nodes()
    assert datas is not None
    assert nodes is not None
    assert ",".join([str(x) for x in v.nodes()]) == 'a,b,c,d'

def test_init_node():
    v, g, record = new_visitor(sorting=True, extra_data={'extra': 1})
    # test the properties of init_node
    assert v.init_node(None,None) == None
    assert v.init_node(nid='a').g == g
    assert v.init_node(nid='a').nid == 'a'
    assert v.init_node(nid='a').n.id() == 'a'
    assert v.init_node(nid='a').d is not None
    assert v.init_node(nid='a').o is None
    assert v.init_node(nid='a').i == -1
    assert v.init_node(nid='a').v is None
    assert v.init_node(nid='a').extra == 1

def test_init_data():
    v, g, record = new_visitor(sorting=True)
    datas = v.Visit()
    assert len(v.datas.keys()) == len(g.nodes())

def test_visit_node():
    v, g, record = new_visitor(data={'a-c':'ac','b-a':'ba'}, sorting=True)
    a = g.node('a')
    b = g.node('b')
    c = g.node('c')
    assert None not in [a,b,c]
    v.Visit()

    verb(pformat(record))
    assert record.origins['c'] == a
    assert record.origins['b'] is None
