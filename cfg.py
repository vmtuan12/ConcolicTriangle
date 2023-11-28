from staticfg import CFGBuilder, Link, Block, CFG
import networkx as nx
import ast
import matplotlib.pyplot as plt
import random

sourceFile = open("test.py", "r")
code = sourceFile.read()

tree = ast.parse(code)

builder = CFGBuilder().build('test cfg', tree)

nx_cfg = nx.DiGraph()

def make_cfg(graph, block, visited, calls=True):

    if block.id in visited:
        return
    
    nodelabel = block.get_source()

    graph.add_node(nodelabel)
    visited.append(block.id)

    for exit in block.exits:
        
        make_cfg(graph, exit.target, visited, calls=calls)
        condition = exit.get_exitcase().strip()
        graph.add_edge(nodelabel, exit.target.get_source(), cond=condition)


entry = None
for block in builder:
    if len(block.exits) == 0:
        nx_cfg.add_node(block.get_source())
    else:
        entry = block
        break

make_cfg(nx_cfg, entry, visited=[], calls=True)

# for x in nx_cfg.edges.data():
#     print(x)

for x in nx_cfg.nodes:
    print('source: ' + x)
    neighbors = nx_cfg[x].keys()
    for nei in neighbors:
        print(nei)
    print('\n')
