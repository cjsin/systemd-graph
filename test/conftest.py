# NOTE: this file is a kind of code-based global configuration for pytest

import sys

sys.dont_write_bytecode = True


# from visitor import *
# from graph import *
# from pprint import pformat, pprint
# from testutil import *
# import pytest

# class CycleItem(pytest.Item):
#     def __init__(self, name, parent, spec):
#         super().__init__(name, parent)

#     def runtest(self):
#         assert 'expected' in self.spec
#         assert 'data' in self.spec
#         expected = self.spec.expected
#         data = self.spec.data
#         assert 'graph' in data
#         graph_edges = data.graph
#         graph = load_graph(self.name, graph_edges)
#         cyclic, cycles = CycleDetection.cyclic_nodes(graph)
#         cstr = ",".join(sorted(cycles.keys()))
#         print(cstr)
#         if cstr != expected:
#             raise YamlException(self, expected, cstr)

# def pytest_collect_file(parent, path):
#     if path.ext == ".yml" and path.basename.startswith("test_cycle"):
#         print(f"Collecting {path}")
#         return CycleFile(path, parent)
#     else:
#         print(f"do not collect {path}")

# class CycleFile(YamlFile):
#     def collect(self):
#         self._collect(CycleItem)
