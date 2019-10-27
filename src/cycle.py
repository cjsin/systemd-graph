from visitor import *
from graph import *
from util import ep

class CycleDetection:

    #example: ClassVar[int] = 4

    @staticmethod
    def template_func(data: dict):
        return {'count':0, 'cycle':0}

    @staticmethod
    def walk_cycle(data: dict, origin: Node) -> NodeList:
        nid = data.nid
        verb(f"Walking back along a cycle from {nid}, prior={origin}")
        seq = [data.n]
        prior_node = origin
        cycle_infos = data.get('cycle_infos',[])
        cycle_infos.append(seq)
        data.cycle_infos = cycle_infos
        dataset = data.d
        oid = origin.id()
        max_iter = 100
        itern = 0
        while origin is not None and oid != nid:
            seq.insert(0,origin)
            if itern >= max_iter:
                log.error(f"Breaking out of loop - either loop is too big (max = {max_iter}) or there is a bug.")
                break
            itern += 1
            pdata = data.d[oid]

            pdata.cycle += 1
            pdata.cycle_infos = cycle_infos
            origin = pdata.o
            if origin is None:
                verb(f"Walking back, did not find cycle node {nid}, reached start of this iteration at {oid} ")
                break
            last = oid
            oid = origin.id()
            if oid == last:
                verb("self loop while walking back!")
                break
            #verb(f"next prior is {origin}")
        verb("Cycle(length "+str(len(seq))+"):"+"->".join([str(x) for x in seq]))
        return seq

    @staticmethod
    def visit_func(data: dict,iteration: int,origin: Node, steps: int):
        di = data.i
        n = data.n
        if not n:
            log.error(f"ERROR: no node for {data}")
            return False
        nid = data.nid
        visting = data.v

        verb(f"{nid} data iteration={di} step {steps} while iteration={iteration}")
        if di == iteration:
            verb(f"Iteration {iteration}[{steps}] - Found a cycle - Node {nid} was already visited in iteration {iteration}. Arrived via {origin}. Left last time via {data.v}")
            data.cycle+=1
            CycleDetection.walk_cycle(data,origin)
            return False
        elif data.count:
            verb(f"This node was already visited in a previous iteration ({di})")
            return False
        else:
            data.count += 1
            return True

    @classmethod
    def cyclic_nodes(cls,g: Graph):
        v = Visitor(g, CycleDetection.template_func, CycleDetection.visit_func)
        datas = v.Visit()
        cycles = AttrDict()
        cyclic = AttrDict()
        for nid, data in datas.items():
            c = data.get('cycle', None)
            cis = data.get('cycle_infos', None)
            if c:
                cyclic[nid] = data
            if cis:
                for ci in cis:
                    s = "->".join([x.id() for x in ci])
                    cycles[s] = ci
        return cyclic, cycles

