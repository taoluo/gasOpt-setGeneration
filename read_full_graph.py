# Copyright (C) 2023 Tao Luo <taoluo71@cis.upenn.edu>

import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint
# from main import node_label
from utils import traceback_upstream_dag, plot_graph


def node_label(n_id, G):
    if isinstance(n_id, str):
        return G.nodes[n_id]['label']
    else:
        res = []
        for n in n_id:
            res.append(node_label(n, G))
        return res


# g = nx.read_graphml("/Users/tao/Projects/wallet.graphml")

g = nx.read_graphml("/Users/tao/Projects/NFT.graphml")

# https://stackoverflow.com/questions/21978487/improving-python-networkx-graph-layout

# def plot_graph(g, node_label_mapping_g=None):
#     # global pos
#     pos = nx.nx_agraph.graphviz_layout(g, prog='neato')
#     nx.draw(g, pos, with_labels=True, font_weight='normal',  labels=node_label_mapping_g)
#     plt.show()


plot_graph(g)

node_label_mapping_g = {}
for n in g.nodes:
    node_label_mapping_g[n] = g.nodes[n]['label']

if __name__ == '__main__':
    recv_txn_rel = set()
    txn_head = set()

    for n in g.nodes():
        if g.nodes[n]['label'].startswith('recv_'):
            recv_txn_rel.add(n)
    print('\n\nrecv_txn_rel')
    pprint(node_label(recv_txn_rel, g))

    for n in recv_txn_rel:
        for succ in g.successors(n):
            txn_head.add(succ)

    print('\n\ntxn_head')
    pprint(node_label(txn_head, g))

    direct_dependency_set_all = set()
    txn_rule_set = set()

    for n in g.nodes:
        if g.nodes[n]['label'].startswith('recv_'):
            for succ in g.successors(n):
                # print(g.get_edge_data(n,succ))
                txn_rule_set = txn_rule_set.union(set(g.get_edge_data(n, succ)['label'].split(' ')))

    print('\n\n\ntxn_rule_set')
    pprint(txn_rule_set)

    for thead in txn_head:

        for pred in g.predecessors(thead):
            # print(pred)
            if not g.nodes[pred]['label'].startswith('recv_'):
                overlap_txn_rule = txn_rule_set.intersection(set(g.get_edge_data(pred, thead)['label'].split(' ')))
                if len(overlap_txn_rule) != 0:
                    direct_dependency_set_all.add(pred)

    print('\n\ndirect_dependency_set_all')
    pprint(node_label(direct_dependency_set_all, g))

    # for n in direct_dependency_set_all:

    g_upstream = traceback_upstream_dag(direct_dependency_set_all, txn_head, g)

    # print(g_upstream)

    node_label_mapping_g_upstream = {}
    for n in g_upstream.nodes:
        node_label_mapping_g_upstream[n] = g_upstream.nodes[n]['label']

    pos = nx.nx_agraph.graphviz_layout(g_upstream, prog='sfdp')

    nx.draw(g_upstream, pos, with_labels=True, font_weight='normal', )  # labels=node_label_mapping_g_upstream)
    plt.show()

    # for n in g_upstream.nodes:
    # print(node_label('n0',g_upstream))
