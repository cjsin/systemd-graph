import sys
import os
import re
from collections import OrderedDict
import util
from util import capture, verb, ep, verbose, Named
from pprint import pprint,pformat
from graph import *
from formatters import *
import traceback
from filters import *
from attrdict import AttrDict
#Node, Label, Edge, Graph, CycleDetection, Visitor, GraphAnalyzer, GraphFilter, CycleFilter, RimFilter, SinkFilter, SourceFilter, LeafFilter, GVFormatter
import traceback

class SystemdBackend:
    def list_units(self):
        pass
    def unit_property(self, unit, kind):
        pass
    def load(self):
        pass
    def save(self):
        pass

class CacheBackend(SystemdBackend):
    DEFAULT_FILE=".systemd-cache.yml"
    def __init__(self, backend=None, file=None):
        if file is None:
            file=CacheBackend.DEFAULT_FILE
        elif file == '':
            # explicitly disabled caching
            ep("Caching disabled for CacheBackend")
        self.file = file
        if backend is None:
            backend = LiveBackend()
        self.backend = backend
        self.data = {}
        # TODO - load yaml file
        if self.file and os.path.exists(self.file):
            self.load()

    def __str__(self):
        return "Cache({})".format(self.file)

    def load(self):
        if not self.file:
            return False

        #ep(f"Load cache {self.file}")
        import yaml
        try:
            with open(self.file,"r") as f:
                strdata = f.read()
                yamldata = yaml.safe_load(strdata)
                self.data = AttrDict()
                self.data.update(yamldata)
                #ep("Loaded cache "+pformat(self.data))
                self.modified = False
                return True
        except:
            traceback.print_exc()
            return False

    def save(self):
        """ Save, if this backend has the capability """
        if not self.file:
            return False
        if not self.modified:
            #ep(f"Skip saving - no changes.")
            return True
        #ep(f"Save cache {self.file}")
        # TODO - save yaml file
        import yaml
        try:
            ydata = dict()
            #ep(f"Save cache self data has {len(self.data.keys())} keys")
            ydata.update(self.data)
            strdata = yaml.safe_dump(ydata)
            with open(self.file,"w") as f:
                f.write(strdata)
                #ep(f"Save cache {len(ydata.keys())}")
                self.modified=False
                return True
        except:
            traceback.print_exc()
            ep("Saving failed.")
            return False

    def load_units(self):
        prop = 'unit-list'
        if prop not in self.data:
            self.data[prop] = self.backend.load_units()
            self.modified=True
            self.save()
        return self.data[prop]

    def unit_property(self, name, kind):
        prop = name + "."+kind
        if prop not in self.data:
            #ep("Call live backend for data")
            self.data[prop] = self.backend.unit_property(name, kind)
            self.modified=True
            #ep(f"Update cache self data has {len(self.data.keys())} keys")
        #ep("return " + pformat(self.data[prop]))

        return self.data[prop]

class LiveBackend(SystemdBackend):
    SSH           = [ "ssh" ]
    COMMON        = [ "--no-legend", "--no-pager", "--full" ]
    LIST_UNITS    = [ "systemctl", "list-units", "--plain", "--all" ] + COMMON
    SHOW_PROPERTY = [ "systemctl", "show", "--value"] + COMMON + [ "--property" ]

    def __init__(self,remote=None,ssh=None):
        self.units    = OrderedDict()
        if isinstance(ssh, str):
            ssh = [ssh]

        if not ssh:
            ssh = LiveBackend.SSH

        ssh = (ssh + [remote]) if remote else []
        self.ssh      = ssh

    def _cmd(self,cmd):
        return self.ssh + cmd

    def _capture(self,cmd):
        return capture(self._cmd(cmd))

    def load_units(self):
        units = {}
        data = self._capture(LiveBackend.LIST_UNITS)
        for l in data:
            name, load, active, sub, *descr = l.split(None,5)
            units[name]={'name': name, 'load': load, 'active': active, 'sub': sub, 'descr': descr }
        return units

    def unit_property(self, name, kind):
        escaped_name = [ '--', name ] if name.startswith('-') else [ name ]
        verb(2, "Escaped name for '{}' is {}".format(str(name), pformat(escaped_name)))
        result = self._capture(LiveBackend.SHOW_PROPERTY + [ kind ] + escaped_name)
        if result:
            other_names = result[0].strip().split(' ')
            if len(other_names) > 1 or other_names[0] != '':
                return other_names
        return []
