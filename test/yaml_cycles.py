
import sys


from visitor import *
from graph import *
from pprint import pformat, pprint
from testutil import *
import pytest
from util import *
from cycle import CycleDetection

def pytest_collect_file(parent, path):
    if path.ext == ".yml" and path.basename.startswith("test_cycle"):
        return CycleFile(path, parent)

class CycleItem(YamlItem):
    def runtest(self):
        assert 'expected' in self.spec
        expected = self.spec['expected']

        if not 'cycles' in expected:
            return

        expected_cycles = expected['cycles']

        assert 'data' in self.spec
        data = self.spec['data']

        assert 'graph' in data
        graph_edges = data['graph']

        graph = load_graph(self.name, graph_edges)
        cyclic, cycles = CycleDetection.cyclic_nodes(graph)
        cstr = ",".join(sorted(cycles.keys()))
        print(cstr)
        if cstr != expected_cycles:
            #ep(f"Mismatch between actual {cstr} and expected {expected_cycles}")
            raise YamlException(self, expected_cycles, cstr)
        else:
            ep("test passed?")

class CycleFile(YamlFile):
    def collect(self):
        yield from self._collect(CycleItem)

