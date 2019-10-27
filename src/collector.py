from collections import OrderedDict

class Collector:
    def __init__(self):
        self.units=OrderedDict()
        self.systemd=Systemd()

    def collect_units(self):
        for u in self.systemd.units():
            self.units[u]=self.systemd.unit(u)

    def collect(self):
        self.collect_units()

