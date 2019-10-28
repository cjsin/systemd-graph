import util
from unit import Unit
from systemd import SystemdGVFormatter, Systemd
from filters import *
from backend import CacheBackend, LiveBackend
import argparse

XDOT = 'xdot'

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

def err(s):
    print("ERROR:"+s, file=sys.stderr)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, help="Increase verbosity")
    parser.add_argument("--cache", type=str, default="systemd-data-REMOTE.yml", help="Specify a cache file")
    parser.add_argument("--out", type=str, default=None, help="Write to this output file - supports template tokens REMOTE,DATE,TIME,SETTINGS,EPOCH")
    parser.add_argument("--clean", action='store_true', help="Delete the cache file first, if it exists")
    parser.add_argument("--relationships", type=str,default='',help="systemd relationships Requires,Before,After etc")
    parser.add_argument("--remote", type=str,default=None, help="A remote host to connect to over ssh")
    parser.add_argument("--ssh", type=str,default='ssh', help="The ssh command to use")
    parser.add_argument("--prune",action='append',default=[],help="Filter out graph nodes based on unit name")
    parser.add_argument("--rim", action='store_true', help="Filter out nodes on the rim of the graph")
    parser.add_argument("--backwards", action='store_true', help="Search backwards for links")
    parser.add_argument("--jobs", type=int,default=1, help="Set the number of parallel jobs")
    parser.add_argument("--leafs", type=int,default=None, help="Filter out leaf nodes (single entry/exit edge). You can specify multiple iterations.")
    parser.add_argument("--cycles", action='store_true', help="Filter out every node that does not participate in a cycle")
    parser.add_argument("--view", action='store_true', help="Run a viewer on the file after generation")
    parser.add_argument("--units",action='append',default=[], help="Start with a subset of units. Specify multiple of all,loaded,exited,dead, and so on, or unit name regex matchers")
    parser.add_argument("--viewer", type=str, default=XDOT, help="Specify the viewer application")
    parser.add_argument("--requires", action='store_true', default=None)
    parser.add_argument("--wants", action='store_true', default=None)
    parser.add_argument("--wantedby", action='store_true', default=None)
    parser.add_argument("--before", action='store_true', default=None)
    parser.add_argument("--after", action='store_true', default=None)
    parser.add_argument("--requires-mounts", action='store_true', default=None)

    parser.add_argument("--active", action='store_true', default=None)
    parser.add_argument("--inactive", action='store_true', default=None)
    parser.add_argument("--dead", action='store_true', default=None)
    parser.add_argument("--running", action='store_true', default=None)
    parser.add_argument("--loaded", action='store_true', default=None)
    parser.add_argument("--not-loaded", action='store_true', default=None)
    parser.add_argument("--listening", action='store_true', default=None)
    parser.add_argument("--mounted", action='store_true', default=None)
    parser.add_argument("--plugged", action='store_true', default=None)

    args = parser.parse_args(argv)
    return parser, args

def main():
    parser, args = parse_args(sys.argv[1:])
    try:

        kinds=Unit.STATUS

        startwith=[]
        if args.units:
            startwith=[]
            for u in args.units:
                if u in ['all']+kinds:
                    startwith.append(u)
                else:
                    startwith.append(re.compile(u))

        if args.active:
            startwith.append('active')
        if args.inactive:
            startwith.append('inactive')
        if args.dead:
            startwith.append('dead')
        if args.running:
            startwith.append('running')
        if args.loaded:
            startwith.append('loaded')
        if args.not_loaded:
            startwith.append('not-loaded')
        if args.listening:
            startwith.append('listening')
        if args.mounted:
            startwith.append('mounted')
        if args.plugged:
            startwith.append('plugged')

        if not startwith:
            startwith=['all']

        sb =  LiveBackend(remote=args.remote,ssh=args.ssh)

        if args.clean:
            if os.path.exists(args.cache):
                os.unlink(args.cache)

        cachefile = args.cache
        if 'REMOTE' in cachefile:
            cachefile = cachefile.replace('REMOTE', args.remote if args.remote else 'localhost')

        cb = CacheBackend(backend=sb, file=cachefile)

        rel_names=''
        processing = set(list(Unit.REQUIRES_RELATIONSHIPS))
        if args.requires is not None \
            or args.wantedby is not None \
                or args.wants is not None \
                    or args.before is not None \
                        or args.after is not None \
                            or args.requires_mounts is not None:
            processing = set()
            if args.requires is not None:
                processing.add(Unit.REQUIRES)
            if args.wants is not None:
                processing.add(Unit.WANTS)
            if args.wantedby is not None:
                processing.add(Unit.WANTEDBY)
            if args.before is not None:
                processing.add(Unit.BEFORE)
            if args.after is not None:
                processing.add(Unit.AFTER)
            if args.requires_mounts is not None:
                processing.add(Unit.MOUNTS)

        if args.relationships:
            if 'all' in args.relationships.split(','):
                rel_names='all'
                processing = processing + set(list([ x for x in Unit.ALL_RELATIONSHIPS]))
            elif args.relationships:
                processing = processing + set(list(args.relationships.split(',')))

        for p in processing:
            if p not in Unit.RELATIONSHIPS:
                err("Invalid relationship name:"+p)
                parser.print_help()
                sys.exit(1)

        rel_names = ''.join([x[0] for x in ['M' if y == Unit.MOUNTS else y for y in processing]])

        s = Systemd(backend=cb, processing=list(processing))
        ep("Building:"+pformat(startwith))
        nodes = s.search(kinds=startwith)
        #ep(pformat(nodes))
        g = s.Graph("test",backwards=args.backwards,units=nodes)
        result = g
        changes=0

        filter_names=[]
        if args.prune:
            prune = PRUNE if 'defaults' in args.prune else []
            prune.extend(list(set(args.prune)  - set('defaults')))
            filter_names.append('p')
            if args.verbose:
                ep("Prune list is:")
                print_lines(["    "+x for x in prune], file=sys.stderr)
            result, changes2 = NodeNameFilter(prune).filter(result)
            changes+=changes2

        if args.cycles:
            filter_names.append('c')
            result, changes2 = CycleFilter().filter(result)
            changes+=changes2

        if args.leafs:
            filter_names.append('l')
            result, changes2 = RepeatFilter(LeafFilter(),-args.leafs).filter(result)
            changes+=changes2

        if args.rim:
            filter_names.append('r')
            result, changes2 = RimFilter().filter(result)
            changes+=changes2

        formatter = SystemdGVFormatter()
        dot_lines = formatter.graph(result)

        outfile=args.out

        settings = rel_names
        if filter_names:
            settings += '-'+''.join(filter_names)

        if outfile is None or args.out == '':
            if args.view:
                import tempfile
                outfile = tempfile.mktemp(suffix=".dot", prefix="systemd-deps-"+settings+".XXXXXX")
        elif outfile == 'stdout':
            outfile = sys.stderr
        elif outfile  == 'stderr':
            outfile = sys.stdout
        else:
            if '-SETTINGS' in outfile:
                outfile = outfile.replace('-SETTINGS','-'+settings if settings else '')
            elif 'SETTINGS' in outfile:
                outfile = outfile.replace('SETTINGS',settings)

            if '-REMOTE' in outfile:
                outfile = outfile.replace('-REMOTE','-'+args.remote if args.remote else '')
            elif 'REMOTE' in outfile:
                outfile = outfile.replace('REMOTE',args.remote if args.remote else '')

            import datetime;
            now = datetime.datetime.now()
            epoch = now.timestamp()
            datestr = now.strftime("%Y%m%d")
            timestr = now.strftime("%H%M%S")
            if 'EPOCH' in outfile:
                #epoch = str(int(time.time()))
                outfile = outfile.replace('EPOCH',str(int(epoch)))
            if 'DATE' in outfile:
                outfile = outfile.replace('DATE',datestr)
            if 'TIME' in outfile:
                outfile = outfile.replace('TIME',timestr)

        if isinstance(outfile, str):
            with open(outfile,"w") as f:
                print_lines(dot_lines, file=f)
                ep("Wrote "+outfile)
            if args.view:
                import subprocess
                subprocess.run(args.viewer.split(' ') + [outfile])
        else:
            if args.view:
                err("View mode is incompatible with output to stdout/stderr")
            print_lines(dot_lines, file=outfile)

    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()


