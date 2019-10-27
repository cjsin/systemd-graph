import util
from unit import Unit
from systemd import SystemdGVFormatter, Systemd
from filters import *
from backend import CacheBackend, LiveBackend
import argparse

PRUNE=[
    "^GEN-.*",
    "^user-.*",
    "[.]scope$",
    "[.]slice$",
    "[.]timer$",
    "[.]swap$",
    #"[.]socket$",
    "[.]device$",
    "^dev-",
    "^run-.*",
    "^user@",
    "^proc-",
    "dev-disk.*",
    "emergency.target",
    "rescue.target"
]

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int)
    parser.add_argument("--clean", action='store_true')
    parser.add_argument("--relationships", type=str,default='')
    args = parser.parse_args(argv)
    return args

def main():
    args = parse_args(sys.argv[1:])
    try:
        sb = LiveBackend()
        cb = CacheBackend(backend=sb)
        processing = Unit.REQUIRES_RELATIONSHIPS
        if 'all' in args.relationships.split(','):
            processing = Unit.ALL_RELATIONSHIPS
        elif args.relationships:
            processing = args.relationships.split(',')

        s = Systemd(backend=cb, processing=processing)
        g = s.Graph("test")
        result = g
        changes=0

        result, changes2 = NodeNameFilter(PRUNE).filter(result)
        changes+=changes2

        #result, changes2 = CycleFilter().filter(result)
        #changes+=changes2

        #result, changes2 = RepeatFilter(LeafFilter(),-6).filter(result)
        #changes+=changes2

        #result, changes2 = RimFilter().filter(result)
        #changes+=changes2
        formatter = SystemdGVFormatter()
        dot_lines = formatter.graph(result)
        print_lines(dot_lines)
    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()


