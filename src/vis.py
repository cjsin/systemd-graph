#!/bin/env python3

import argparse
import sys
import pyvis
import os
from pyvis.network import Network
import networkx as nx
import pandas as pd
from util import ep

class Vis(Network):
    DEFAULTS=dict(height="750px", width="100%", bgcolor="#222222", font_color="white")

    def __init__(self,**kwargs):
        kw = {}
        kw.update(Vis.DEFAULTS)
        kw.update(kwargs)
        super().__init__(**kw)
        os.environ['BROWSER']='chromium'
        self.path =os.path.dirname(__file__) + "/html/vis_template.html"

def save_dotfile(dotfile, htmlfile, show=False):

    #net.toggle_physics()
    #net.show("blah.html")

    if dotfile:
        net = Vis()
        #net.show_buttons(filter_=['physics'])

        ep("Load " + dotfile)
        net.from_DOT(dotfile)
        ep("Number of edges:{}".format(net.num_edges()))
        if show:
            net.show(htmlfile)
        else:
            net.save_graph(htmlfile)

    else:
        ep("No file.")

def go(args):
    os.environ['BROWSER']='chromium'
    net = Vis()
    net.add_node(1, label="Node 1")
    net.add_node(2)
    nodes = ["a", "b", "c", "d"]
    net.add_nodes(nodes)  #node ids and labels = ["a", "b", "c", "d"]
    net.add_nodes("hello") # node ids and labels = ["h", "e", "l", "o"]
    #["size", "value", "title", "x", "y", "label", "color"]

    #net.add_nodes([1,2,3], value=[10, 100, 400], title=["I am node 1", "node 2 here", "and im node 3"], x=[21.4, 54.2, 11.2], y=[100.2, 23.54, 32.1], label=["NODE 1", "NODE 2", "NODE 3"], color=["#00ff1e", "#162347", "#dd4b39"])
    #net.add_node(0, label="a")
    #net.add_node(1, label="b")
    #net.add_edge(0, 1)

    #nxg = nx.complete_graph(10)
    #G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    #G.from_nx(nxg)

    #net.enable_physics(True)
    net.path =os.path.dirname(__file__) + "/html/vis_template.html"
    #net.toggle_physics()
    #net.show("blah.html")

    if args.dotfile:
        Vis()
        ep("Load " + args.dotfile)
        net.from_DOT(args.dotfile)
        ep("Number of edges:{}".format(net.num_edges()))
        net.show("test.dot.html")
    else:
        ep("No file.")

    # got_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    # # set the physics layout of the network
    # got_net.barnes_hut()
    # got_data = pd.read_csv("https://www.macalester.edu/~abeverid/data/stormofswords.csv")

    # sources = got_data['Source']
    # targets = got_data['Target']
    # weights = got_data['Weight']

    # edge_data = zip(sources, targets, weights)

    # for e in edge_data:
    #     src = e[0]
    #     dst = e[1]
    #     w = e[2]

    #     got_net.add_node(src, src, title=src)
    #     got_net.add_node(dst, dst, title=dst)
    #     got_net.add_edge(src, dst, value=w)

    # neighbor_map = got_net.get_adj_list()

    # # add neighbor data to node hover data
    # for node in got_net.nodes:
    #     node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
    #     node["value"] = len(neighbor_map[node["id"]])

    # got_net.show("gameofthrones.html")
    # net.show_buttons(filter_=['physics'])

    # nt.Network("500px", "500px")
    # nt.from_DOT("test.dot")
    # nt.show("dot.html")
    # nx_graph = Networkx.cycle_graph()
    # nt = Network("500px", "500px")
    # # populates the nodes and edges data structures
    # nt.from_nx(nx_graph)
    # nt.show("nx.html")
    # net.prep_notebook()
    # net.show("nb.html")
    #  net.save_graph(htmlfilename)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('dotfile', nargs='?', default=None)

    args = parser.parse_args(args)
    return args, parser

def main(argv):
    args, parser = parse_args(argv)
    go(args)

if __name__ == "__main__":
    main(sys.argv[1:])
