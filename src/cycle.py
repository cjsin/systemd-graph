from visitor import *
from graph import *
from util import ep

class CycleDetection:

    #example: ClassVar[int] = 4

    @staticmethod
    def template_func(data: dict):
        return {'count':0, 'cycle':0}

    @staticmethod
    def walk_cycle(data: dict) -> NodeList:
        nid = data.nid
        start = nid
        verb(f"Walking forward along a cycle from {nid}")
        seq = [data.n]
        cycle_infos = data.get('cycle_infos',[])
        cycle_infos.append(seq)
        data.cycle_infos = cycle_infos
        dataset = data.d
        max_iter = 100
        itern = 0
        v = data.v
        while v is not None and v.nid != nid:
            seq.append(v.n)
            if itern >= max_iter:
                log.error(f"Breaking out of loop - either loop is too big (max = {max_iter}) or there is a bug.")
                break
            itern += 1
            v.cycle += 1
            # add this cycle to this node
            vci = v.get('cycle_infos',[])
            vci.append(seq)
            v.cycle_infos=vci
            if v.v is None:
                verb(f"Walking back, did not find cycle node {nid} after reaching {v.nid}")
                break
            v = v.v
        verb("Cycle(length "+str(len(seq))+"):"+"->".join([str(x) for x in seq]))
        return seq

    @staticmethod
    def visit_func(data: dict,iteration: int,origin: Node, steps: int):
        di = data.i
        n = data.n
        if not n:
            verb(f"ERROR: no node for {data.nid}")
            return False
        nid = data.nid
        visting = data.v

        verb(f"{nid} data iteration={di} step {steps} while iteration={iteration}")
        if di == iteration:
            verb(f"Iteration {iteration}[{steps}] - Found a cycle - Node {nid} was already visited in iteration {iteration}. Arrived via {origin}. Left last time via {data.v}")
            data.cycle+=1
            #CycleDetection.walk_cycle(data,origin)
            CycleDetection.walk_cycle(data)
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

