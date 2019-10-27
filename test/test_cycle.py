import pytest
from visitor import *
from graph import *
from pprint import pformat, pprint
from testutil import load_graph
from util import ep, print_lines
from cycle import CycleDetection
from formatters import GVFormatter

#@pytest.mark.slow
def test_cycle():
    g = load_graph("test-cycle", {'a-b':'ab','b-c':'bc','f-a':'fa','c-e':'ce','e-b':'eb','f-d':'fd'})
    cyclic,cycles = CycleDetection.cyclic_nodes(g)
    cstr = ",".join(sorted(cycles.keys()))
    print_lines(GVFormatter().graph(g))
    print(cstr)
    assert cstr == 'c->e->b'
    # a = Node("a")
    # b = Node("b")
    # c = Node("c")
    # d = Node("d")
    # e = Node("e")
    # f = Node("f")
    # g.add_node(a)
    # g.add_node(b)
    # g.add_node(c)
    # g.add_node(d)
    # g.add_node(e)
    # g.add_node(f)

    # g.add_edge(a.add_edge(b))
    # g.add_edge(b.add_edge(c))
    # g.add_edge(f.add_edge(a))
    # g.add_edge(c.add_edge(e))
    # g.add_edge(e.add_edge(b))
    # g.add_edge(f.add_edge(d))

if __name__ == "__main__":
    test_cycle()
