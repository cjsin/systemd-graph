
import sys

from visitor import *
from graph import *
from pprint import pformat, pprint
from testutil import *
import pytest
from util import *
from cycle import CycleDetection

class BatteryException(Exception):
    """ custom exception for error reporting. """

def battery_check(g):
    c = g.check()
    ep(pformat(c))
    assert not g.check()

def battery_cycles(g, expected):
    cyclic, cycles = CycleDetection.cyclic_nodes(g)
    cstr = ",".join(sorted(cycles.keys()))
    assert cstr == expected

def battery_counts(g, expected):
    assert g.nodecount() == expected['nodecount']
    assert g.edgecount() == expected['edgecount']

def battery(item, g, expected):
    try:
        battery_check(g)
        if 'cycles' in expected:
            battery_cycles(g, expected['cycles'])
        if 'counts' in expected:
            battery_counts(g, expected['counts'])
    except:
        ep("Failed!")
        import traceback
        traceback.print_exc()
        raise BatteryException(item)

class BatteryItem(YamlItem):
    def runtest(self):
        assert 'expected' in self.spec
        expected = self.spec['expected']

        assert 'data' in self.spec
        data = self.spec['data']

        assert 'graph' in data
        g = load_graph(self.name, data['graph'])
        assert g is not None

        battery(self, g, expected)

def pytest_collect_file(parent, path):
    #ep(f"path={path}")
    if path.ext == ".yml" and path.basename.startswith("test_") and path.basename.endswith("_cases.yml"):
        return BatteryFile(path, parent)

class BatteryFile(YamlFile):
    def collect(self):
        return self._collect(BatteryItem)

