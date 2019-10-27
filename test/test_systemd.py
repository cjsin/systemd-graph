import pytest
from systemd import *

@pytest.fixture
def sd():
    s = Systemd()
    return s
