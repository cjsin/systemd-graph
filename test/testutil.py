import pytest
from graph import Graph,Node,Edge,Label
from formatters import GVFormatter
from util import print_lines, ep
from pprint import pformat

def dump_graph(g):
    print_lines(GVFormatter().graph(g))

def load_graph(name, test_data):
    ga,gb=load_graphx(name,test_data)
    #ga fails and gb passes
    print(repr(ga))
    print(repr(gb))
    #assert False
    return gb

def load_graphx(name, test_data):

    ep("Generate ga")
    ga=load_graph1(name, test_data)
    ep(f"ga={ga}")
    ga.check()

    ep("Generate gb")
    gb=load_graph2(name, test_data)
    ep(f"gb={gb}")
    gb.check()

    ep("Compare ga and gb: ")
    assert repr(ga) == repr(gb)
    ep(f"{repr(ga)} == {repr(gb)}")
    return ga,gb

def load_graph1(name, test_data):
    g = Graph(name)
    for edgespec,label in test_data.items():
        a,b = edgespec.split('-')
        # a = g.add_node(Node(a))
        # b = g.add_node(Node(b))
        a = g.node(a) or g.add_node(Node(a))
        b = g.node(b) or g.add_node(Node(b))
        e = g.add_edge(a.add_edge(b))
        e.add_label(label)
    return g

def load_graph2(name,test_data):
    g = Graph(name)
    for edgespec,label in test_data.items():
        a,b = edgespec.split('-')
        a = g.node(a) or g.add_node(Node(a))
        b = g.node(b) or g.add_node(Node(b))
        #a = Node(a)
        #b = Node(b)
        e = g.add_edge(a.add_edge(b))
        e.add_label(label)
    return g

class YamlFile(pytest.File):
    def _collect(self, TestClass):
        import yaml # we need a yaml parser, e.g. PyYAML
        raw = yaml.safe_load(self.fspath.open())
        if ['items'] in raw:
            test_items = raw['items']
            for name, spec in sorted(test_items.keys()):
                yield TestClass(name, self, spec)

class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, YamlException):
            return "\n".join([
                "usecase execution failed",
                "   spec failed: %r: %r" % excinfo.value.args[1:3],
                "   no further details known at this point."
            ])

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name

class YamlException(Exception):
    """ custom exception for error reporting. """

