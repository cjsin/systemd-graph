# NOTE: this file is a kind of code-based global configuration for pytest

import sys

sys.dont_write_bytecode = True


from visitor import *
from graph import *
from pprint import pformat, pprint
from testutil import *
import pytest
from util import *
from cycle import CycleDetection

import yaml_cycles
import yaml_battery

def pytest_collect_file(parent, path):
    check = yaml_cycles.pytest_collect_file(parent, path)
    if check is not None:
        return check
    check = yaml_battery.pytest_collect_file(parent, path)
    if check is not None:
        return check
