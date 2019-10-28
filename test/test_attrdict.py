import pytest
from util import ep
from pprint import pformat
from attrdict import AttrDict
from random import randrange

def test_attrdict_defaults():

    a = AttrDict()

    assert a is not None

    assert a.get('xyz', None) is None
    assert a.get('abc','def') == 'def'
    a['mno']='pqr'
    assert a.get('mno','stu') == 'pqr'

def test_attrdict_defaults():

    a = AttrDict()
    assert a.items() is not None

def test_attrdict_del():
    a = AttrDict()
    a['mno']='pqr'
    assert len(a.keys()) == 1
    assert len(a.values()) == 1

    del a['mno']
    assert len(a.keys()) == 0
    assert len(a.values()) == 0

def test_attrdict_items():
    a = AttrDict()
    a['mno']='pqr'
    for i in a.items():
        assert isinstance(i,tuple)

def test_ordered():
    inserted=[]
    a = AttrDict()
    for n in range(1,5):
        v = randrange(0,100)
        a[str(v)]=len(inserted)
        inserted.append(str(v))

    assert ",".join(a.keys()) == ",".join(inserted)

