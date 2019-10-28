import os
import sys
import subprocess
import logging

VERBOSE=0
log = logging.getLogger(__name__)

def set_verbose(n):
    global VERBOSE
    VERBOSE=n

def inc_verbose(n):
    global VERBOSE
    VERBOSE+=n

def verbose():
    global VERBOSE
    return VERBOSE

def ep(s):
    if not isinstance(s,str):
        s=str(s)
    if len(s):
        end='' if s[0] == '\r' else '\n'
        print(s, file=sys.stderr, end=end)

def verb1(*args):
    verb(1,*args)
def verb2(*args):
    verb(2,*args)
def verb3(*args):
    verb(3,*args)
def verb4(*args):
    verb(4,*args)
def verb5(*args):
    verb(5,*args)
def verb6(*args):
    verb(6,*args)
def verb7(*args):
    verb(7,*args)
def verb8(*args):
    verb(8,*args)
def verb9(*args):
    verb(9,*args)

def verb(*args,**kwargs):
    global VERBOSE
    level=None
    s=None
    f=None
    if 'level' in kwargs:
        level=kwargs['level']
    if 's' in kwargs:
        s = kwargs['s']
    if 'f' in kwargs:
        f = kwargs['f']

    if args is None:
        args=[]

    if level is None and len(args) > 1 and isinstance(args[0], int):
        level=args[0]
        s=args[1]
    elif args:
        s=args[0]

    if level is None:
        level=1
    if f is None:
        f=sys.stderr

    if VERBOSE >= level:
        if s is not None:
            print("[verb-"+str(level)+"] "+s, file=f)

def capture(cmd, verbose=False):
    if verbose:
        print("Run:"+" ".join(cmd), file=sys.stderr)
    cproc = subprocess.run(cmd, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, universal_newlines=True)

    if cproc.returncode == 0:
        lines=cproc.stdout.splitlines()
        return lines
    else:
        log.error("Command '{}' failed [status={}]".format(" ".join(cmd), cproc.returncode))
        if cproc.stderr:
            lines = cproc.stderr.splitlines()
            for l in lines:
                log.error("[    "+l+"]")
        return None


def check_environ():
    if 'VERBOSE' in os.environ:
        v=0
        ve=os.environ['VERBOSE']
        if ve.lower() in ['yes','true','on','y','t','1']:
            v=1
        elif ve.lower() in ['no','false','off','n','f','0']:
            v=0
        else:
            try:
                v = int(os.environ['VERBOSE'])
            except:
                log.error("Unrecognised value for VERBOSE:"+ve)
                return
        set_verbose(v)


class Named:
    def __init__(self, name):
        self.name=name
    def id(self):
        return self.__class__.__name__ +"/"+self.name
    def __str__(self):
        return self.id()
    def __repr__(self):
        return self.id()


def print_lines(lines):
    for x in lines:
        print(x)

check_environ()
