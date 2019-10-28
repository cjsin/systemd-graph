from dictobj import MutableDictionaryObject

class AttrDict(MutableDictionaryObject):
    """ extend the dictobj class to be usable like a dict """
    def __init__(self, contents=(), **kwargs):
        super(MutableDictionaryObject, self).__init__(contents,None, **kwargs)

    def update(self, other):
        for k,v in other.items():
            self[k]=v
        return self

    def get(self, key, defval):
        return self[key] if key in self else defval

    def items(self):
        yield from self._items.items()
