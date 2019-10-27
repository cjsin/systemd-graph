from graph import *
from typing import List
StrList = List[str]

class GVFormatter:
    def __init__(self, styles=None):
        if styles is None:
            styles={'shape':'ellipse', 'style':'filled','fillcolor': 'white'}
        self.default_style=styles

    def node(self, n) -> StrList:
        nn=self.node_name(n)
        ns=self.stylise_node(n)
        nss=','.join([k+'='+ns[k] for k in sorted(ns.keys())])
        return [f"{nn} [{nss}];"]

    def stylise_node(self,n):
        ret={}
        ret.update(self.default_style)
        return ret

    def node_name(self, n) -> str:
        t = n.token
        return '"'+t+'"' if re.search(r'[^a-zA-Z0-9_]', t) else t

    def edge_labels(self, e) -> str:
        return "|".join([str(x) for x in e.Labels()])

    def edge(self, e) -> StrList:
        return ['{} -> {} [label="{}"];'.format(self.node_name(e.a), self.node_name(e.b),self.edge_labels(e))]

    def edges(self, arr) -> StrList:
        lines=[]
        for e in arr:
            lines.extend(self.edge(e))
        return lines

    def nodes(self, arr) -> StrList:
        lines=[]
        for n in arr:
            lines.extend(self.node(n))
        return lines

    def graph(self, g) -> StrList:
        lines=[]
        lines.append(f"digraph {g.name} {{")
        lines.append("node [shape=egg,style=solid];")
        lines.extend(self.nodes(g.nodes()))
        lines.extend(self.edges(g.edges()))
        lines.append("}")
        return lines
