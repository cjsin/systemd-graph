from graph import *
from util import *
from analyse import GraphAnalyzer

class GraphFilter:
    def __init__(self):
        pass

    def _filter(self, orig, filtered):
        filtered.add(orig)
        return filtered, 0

    def filter(self, orig):
        nn=orig.nodecount()
        ne=orig.edgecount()
        ret, changes2 = self._filter(orig, Graph(orig.name))
        fn=ret.nodecount()
        fe=ret.edgecount()
        changes = (nn-fn) + (ne-fe)
        #ep(f"{self.__class__.__name__} filtered {nn}n/{ne}e to {fn}n/{fe}e ({changes}/{changes2} changes)")
        return ret, max(changes,changes2)

class AnalysisFilter(GraphFilter):

    def _analysis_filter(self, orig, filtered, analysis):
        return filtered, 0

    def _filter(self, orig, filtered):
        analysis=GraphAnalyzer(orig)
        ret,changes = self._analysis_filter(orig,filtered, analysis)
        return ret,changes

class RepeatFilter(GraphFilter):
    def __init__(self, other_filter, iterations=None):
        if iterations is None:
            iterations=-10
        self.iterations=iterations
        self.other_filter=other_filter

    def _filter(self, orig, filtered):
        iterations=self.iterations
        filtered.add(orig)
        changes=0
        consolidated=False
        maxiter=iterations
        iterations=0
        if maxiter > 0:
            while maxiter:
                filtered,changes2=self.other_filter.filter(filtered)
                maxiter-=1
                iterations+=1
                changes+=changes2
                if not changes2:
                    consolidated=True
                    break
        elif maxiter is None:
            while True:
                filtered,changes2 = self.other_filter.filter(filtered)
                iterations+=1
                changes += changes2
                if not changes2:
                    consolidated=True
                    break
        elif maxiter < 0:
            maxiter = -maxiter
            while maxiter:
                filtered,changes2 = self.other_filter.filter(filtered)
                maxiter-=1
                iterations+=1
                changes += changes2
                if not changes2:
                    consolidated=True
                    break
        if not consolidated:
            ep("Filter reached max iterations before consolidating")
        else:
            #ep(f"Filter consolidated after {iterations} iterations.")
            pass

        fn=filtered.nodecount()
        fe=filtered.edgecount()
        #ep(f"Return graph with {fn}n/{fe}e")
        return filtered, changes

class CycleFilter(AnalysisFilter):
    """
    Filter out anything that is not part of a cycle
    """
    def __init__(self):
        super().__init__()

    def _analysis_filter(self, orig, filtered, analysis):
        changes=0
        kept={}
        cyclic = analysis.cyclic
        ncyclic = len(cyclic)
        #ep(f"Graph has {ncyclic} nodes participating in cycles")
        for n in orig.nodes():
            nid=n.id()
            if nid in analysis.cyclic:
                kept[nid]=n
            else:
                changes+=1

        for nid,n in kept.items():
            filtered.add_node(n)

        for e in orig.edges():
            if e.a.id() in kept and e.b.id() in kept:
                filtered.add_edge(e)
            else:
                changes+=1
        return filtered, changes

class NodeFilter(GraphFilter):
    """
    Filter out nodes then discard edges that use those nodes
    """
    def __init__(self):
        super().__init__()

    def _filter_node(self, orig, n, nid):
        return False

    def _filter(self, orig, filtered):
        changes=0
        nchanges=0
        echanges=0
        kept={}
        for n in orig.nodes():
            nid=n.id()
            discard = self._filter_node(orig, n,nid)
            if not discard:
                kept[nid]=n
            else:
                changes+=1
                nchanges+=1

        for nid,n in kept.items():
            filtered.add_node(n)

        for e in orig.edges():
            if e.a.id() in kept and e.b.id() in kept:
                filtered.add_edge(e)
            else:
                changes+=1
                echanges+=1
        #ep(f"{echanges} edges excluded for {nchanges} nodes.")
        return filtered, changes

class AnalysisNodeFilter(GraphFilter):
    """
    Filter out nodes then discard edges that use those nodes
    """
    def __init__(self):
        super().__init__()

    def _analysis_node_filter(self, orig, analysis, n, nid):
        return False

    def _filter(self, orig, filtered):
        analysis=GraphAnalyzer(orig)
        changes=0
        kept={}
        for n in orig.nodes():
            nid=n.id()
            discard = self._analysis_node_filter(orig, analysis, n,nid)
            if not discard:
                kept[nid]=n
            else:
                changes+=1

        for nid,n in kept.items():
            filtered.add_node(n)

        for e in orig.edges():
            if e.a.id() in kept and e.b.id() in kept:
                filtered.add_edge(e)
            else:
                changes+=1
        return filtered, changes

class NodeNameFilter(NodeFilter):
    def __init__(self,patterns=None,exclude=True):
        if patterns is None:
            patterns=[]
        self.patterns= patterns
        self.res = [ re.compile(r) for r in patterns]
        self.exclude=exclude

    def _filter_node(self, orig, n, nid):
        nn = n.name
        for r in self.res:
            #ep(f"Check {nn} against {r}")
            matched = re.search(r, nn)
            if matched:
                #verb(f"name {nn} matched {r}, return {self.exclude}")
                # Our return value is always whether
                # the node should be filtered (excluded)
                return self.exclude
        # The node did not match, therefore
        # return the opposite of our exclude flag
        return not self.exclude

class NodeNameSearch(NodeFilter):
    def __init__(self,patternsList = []):
        super().__init__(patterns, exclude=False)

class InnyOutyFilter(AnalysisNodeFilter):
    """
    Filter out leaf nodes (1 link only, in or out, cannot be part of a cycle)
    """
    def __init__(self):
        super().__init__()

    def _analysis_node_filter(self, orig, analysis, n, nid):
        i = analysis.ins[nid]
        o = analysis.outs[nid]
        return self._filter_inny_outie(orig, analysis, n, nid, i, o)

    def _filter_inny_outie(self, orig, analysis, n, nid, innies, outies):
        return False

class LeafFilter(InnyOutyFilter):
    """
    Filter out leaf nodes (1 link only, in or out, cannot be part of a cycle)
    """
    def _filter_inny_outie(self, orig, analysis, n, nid, innies, outies):
        return  (innies + outies) < 2

class SinkFilter(InnyOutyFilter):
    """
    Filter out terminal nodes (no out edges, cannot be part of a cycle)
    """
    def _filter_inny_outie(self, orig, analysis, n, nid, innies, outies):
        return outies < 1

class SourceFilter(InnyOutyFilter):
    """
    Filter out source nodes (no in edges, cannot be part of a cycle)
    """
    def __init__(self):
        super().__init__()

    def _filter_inny_outie(self, orig, analysis, n, nid, innies, outies):
        return innies < 1

class RimFilter(InnyOutyFilter):
    """
    Filter out source or sink nodes (cannot be part of a cycle)
    """
    def __init__(self):
        super().__init__()

    def _filter_inny_outie(self, orig, analysis, n, nid, innies, outies):
        return innies < 1 or outies < 1
