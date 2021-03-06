from graph import *
from util import verb
from attrdict import AttrDict
from pprint import pprint, pformat
import logging
log = logging.getLogger(__name__)

class Visitor:
    def __init__(self, g, template_func, visit_func, sorting=True):
        """
        sorting: allow to sort nodes by ID for stable output (useful in writing stable tests)
        """
        self.g=g
        self.idx=0
        self.template_func=template_func
        self.visit_func=visit_func
        self.datas=AttrDict()
        self.sorting=sorting
        self.to_visit=set()

    def nodes(self):
        if self.sorting:
            ids=sorted ([x.id() for x in self.g.nodes()])
            return [self.g.node(x) for x in ids]
        else:
            return self.g.nodes()

    def init_node(self,nid=None,n=None):
        if n is None and nid is None:
            log.error("init_node called with no valid parameter")
            return None
        elif nid is None:
            nid = n.id()
        elif n is None:
            n = self.g.node(nid)
        self.to_visit.add(nid)

        #verb(f"Init node data for {nid}")

        tmpl = AttrDict({
            # Items that stay the same
            'x':   self.idx,
            'g':   self.g,
            'nid': nid,
            'n':   n,
            'd':   self.datas,
            #'visitor': self,
            # Items that are updated during visiting
            'o':   None,
            'i':   -1,
            'v':   None,
        })

        extra = self.template_func(tmpl) if self.template_func else None
        if extra:
            tmpl.update(extra)
        self.datas[nid]=tmpl
        self.idx+=1
        return tmpl

    def init_data(self):
        self.datas = AttrDict()
        self.to_visit=set()
        self.idx = 0
        for n in self.nodes():
            self.init_node(n=n)

    def visit_node(self, data, iteration, origin, steps):
        nid = data.nid
        n   = data.n

        # start with this node and visit it
        #verb(f"here, nid={nid}, n={n}, iter={iteration}, origin={origin}")

        visit_further = self.visit_func(data, iteration, origin, steps)


        # Note that iteration and origin are set *after* the visit function,
        # however the visit function receives those in the function call,
        # it is not set yet in the object so that the visitor an check if there
        # is a pre-existing value. However it is set prior to moving on to the
        # next node, so that the historical value is maintained
        data.i = iteration
        data.o    = origin

        visit_also = []
        if not visit_further:
            verb("Will not visit further from node "+str(nid))
        if visit_further:
            #verb(f"Node {nid} - checking edges.")
            for e in n.Edges():
                verb("Edge {}".format(e))
                if e.b.id == nid:
                    if e.a.id == nid:
                        log.warning("self-loop")
                    else:
                        log.warning("Back-to-front edge!")
                        visit_also.append(e.a.id())
                else:
                    visit_also.append(e.b.id())

            if not visit_also:
                verb("{} is terminal or visitor returned False.".format(nid))
            else:
                verb("Will visit {} nodes from here".format(len(visit_also)))
                if self.sorting:
                    visit_also = sorted(visit_also)
                verb("  Will visit also " + ", ".join(visit_also))

            for vid in visit_also:
                if vid is not None:
                    vdata = data.d.get(vid, None)
                    if not vdata:
                        verb("****BUG***** visitor data for {} not yet initialised - edge to un-indexed node, Creating it.".format(vid))
                        vdata = self.init_node(nid=vid)
                    data.v=vdata
                    self.visit_node(vdata, iteration, n, steps+1)
                data.v=None

    def Visit(self):
        self.init_data()

        # NOTE the set of nodes to visit is used like this
        # because it can grow during the visiting, if new nodes are discovered.
        iteration = 0
        while len(self.to_visit):
            nid = self.to_visit.pop()
            data = self.datas[nid]
            iteration +=1
            verb("Visiting {} with iteration = {} step 0 from nowhere".format(data.nid,iteration))
            self.visit_node(data, iteration, None, 0)
        return self.datas
