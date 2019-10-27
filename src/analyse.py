from collections import Counter
from graph import Graph, Edge, Node, Label
from cycle import CycleDetection

class GraphAnalyzer:
    def __init__(self,g: Graph):
        self.ins : Counter = None
        self.outs : Counter = None
        self.weights : Counter = None
        self.bridges : Counter = None
        self.cyclic : set = None
        self.g: Graph = g
        if g:
            self.Analyse(g)

    def Analyse(self, g):
        self.g=g
        self.ins=Counter()
        self.outs=Counter()
        self.weights=Counter()
        self.bridges=Counter()
        self.cyclic = set()

        #for n in g.nodes():
        #    filtered.add_node(n)
        for e in g.edges():
            aid: str =e.a.id()
            bid: str =e.b.id()
            self.ins[bid]+=1
            self.outs[aid]+=1
            self.weights[aid]+=1
            self.weights[bid]+=1

        for n in g.nodes():
            nid: str =n.id()
            if self.ins[nid] == 1 and self.outs[nid]==1:
                self.bridges[nid]+=1

        self.cyclic = CycleDetection.cyclic_nodes(g)
