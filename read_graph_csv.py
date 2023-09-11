
# recd g from csv file





if __name__ == '__main__':
    from pprint import pprint
    import pandas as pd
    import networkx as nx
    import os
    import json
    import matplotlib.pyplot as plt
    from algo import get_minimal_all,set_of_minimal_relations

    from utils import traceback_upstream_dag, plot_graph, node_label

    # for root, dirs, files in os.walk("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/temp", topdown=False):

    for root, dirs, files in os.walk("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/relation-dependencies", topdown=False):
        for name in files:
            print('\n\n\n\n read csv file ' + name)
            print(os.path.join(root, name))

            datalog_file = os.path.join("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/benchmarks", name.split(".")[0] + '.dl')
            public_relation_readonly = []
            print(os.path.join("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/benchmarks", name.split(".")[0] + '.dl'))
            with open(datalog_file,'r') as dl:
                for l in dl:
                    if '.public' in l and (not 'recv_' in l):
                        public_relation_readonly.append(l.split(' ')[1].split('(')[0])
                        # print('public', public_relation_readonly[-1])
            print('\n\npublic_relation_readonly')
            pprint(public_relation_readonly)
            df = pd.read_csv(os.path.join(root, name),header=0)


            # df = pd.read_csv('./declarative-smart-contracts/relation-dependencies/Tether.csv',header=0)
            # df = pd.read_csv('./declarative-smart-contracts/relation-dependencies/Nft.csv',header=0)

            # construct the g
            txn_head_all = set()
            G = nx.DiGraph()
            for i,r in df.iterrows():
                # G.add_edge(r['#body'], r['head'], is_agg= r['isAgg'], rule_id= r['ruleId'],)
                edge_data = G.get_edge_data(r['#body'], r['head'])

                if edge_data is None:
                    G.add_edge(r['#body'], r['head'], is_agg= r['isAgg'], rule_id= (r['ruleId'],), is_txn=r['isTx'] )
                    if r['isTx']:
                        txn_head_all.add(r['head'])

                else:
                    assert edge_data['is_agg'] == r['isAgg']
                    # assert edge_data['is_txn'] == r['isTx']
                    edge_data['is_txn'] = edge_data['is_txn']  or r['isTx']
                    edge_data['rule_id'] = tuple(sorted(edge_data['rule_id'] +  (r['ruleId'],) ))
                    print(edge_data['rule_id'])
                    print( r['#body'], r['head'], G.get_edge_data(r['#body'], r['head']) )

            # # find txn head relations
            # txn_head_all = set()
            # print('\n\n\ntxn_head_all')
            # for n in G.nodes():
            #     if n.startswith('recv_'):
            #         txn_head_of_n = set(G.successors(n))
            #         # print(txn_head_of_n)
            #         txn_head_all = txn_head_all.union(txn_head_of_n)
            #
            #
            # print(txn_head_all)


            print('\n\n\ntxn_head_all')
            print(txn_head_all)

            # direct dependency relations
            direct_dependency_set_all = set()

            # for n in txn_head_all:
            #     print('\nnode ')
            #     print(n)
            #     print(list(G.predecessors(n)))
            #     dependency = set((i for i in G.predecessors(n) if not i.startswith('recv_')))
            #     direct_dependency_set_all = direct_dependency_set_all.union(dependency )

            for thead in txn_head_all:

                for pred in G.predecessors(thead):
                    print(pred)
                    if G.get_edge_data(pred, thead)['is_txn'] and (not pred.startswith('recv_')):

                        # overlap_txn_rule = txn_rule_set.intersection(set(g.get_edge_data(pred, thead)['label'].split(' ')))
                        # if len(overlap_txn_rule) != 0:
                        direct_dependency_set_all.add(pred)


            print('\n\n\ndirect_dependency_set_all')

            # pprint(direct_dependency_set_all)
            # pos = nx.nx_agraph.graphviz_layout(G, prog='neato')
            #
            # nx.draw(G, pos, with_labels=True, font_weight='normal')
            # plt.show()
            direct_dependency_set_all = direct_dependency_set_all.union(set(public_relation_readonly))

            upstream_dag =  traceback_upstream_dag(direct_dependency_set_all, txn_head=txn_head_all,g=G)
            plot_graph(G)

            plot_graph(upstream_dag)


            mms_from_direct_dependency = set_of_minimal_relations(direct_dependency_set_all, direct_dependency_set_all, upstream_dag)
            print('\n\nmms_from_direct_dependency')
            pprint( node_label(mms_from_direct_dependency, upstream_dag))
            minimal_all = get_minimal_all(mms_from_direct_dependency, direct_dependency_set_all, upstream_dag)
            # minimal_all = []
            print("count minimal_all", len(minimal_all))
            # pprint(a)
            pprint(node_label(minimal_all,upstream_dag))

            # break

            # json_object = json.dumps(list(minimal_all), indent=4)
            df = pd.DataFrame(minimal_all)
            df.to_csv("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/minimal_materialize_set/" + name.split('.')[0]+'.csv', index=False, header=False)
            # with open("/Users/tao/Projects/datalog_graph/declarative-smart-contracts/minimal_materialize_set/" + name.split('.')[0]+'.json', "w") as outfile:
            #     outfile.write(json_object)


