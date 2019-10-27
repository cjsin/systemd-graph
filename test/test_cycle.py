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
    assert cstr == 'b->c->e'

if __name__ == "__main__":
    test_cycle()
