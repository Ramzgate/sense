import numpy as np
import pandas as pd
import datetime

import networkx as nx

#################################################################################################
# 'getFLow' computes the flow through a graph from sink to source constrained by a capacity
# equal to the overall periodic (daily or monthly) flow through each edge, which is equal to the 
# the volume of trade for the pair on a given exchange. 
# 
# This figure is used to normalize the weight on any edge aka the volume over the network flow.
# 
# These computations are based on the Ford Falbkerson algorithm 

def genDiGraph(G,period='m_vol'):
    G0 = nx.Graph()
    for s1,s2 in G.edges:
        G0.add_edge(s1,s2)
        G0[s1][s2]['vol']=G[s1][s2][period]
    return(nx.DiGraph(G0))

def bfs(graph, source, sink):
    queue, visited = [(source, [source])], [source]
    while queue:
        u, path = queue.pop(0)
        edge_nodes = set(graph[u].keys()) - set(path)
        for v in edge_nodes:
            if v in visited:
                continue
            visited.append(v)
            if not graph.has_edge(u, v):
                continue
            elif v == sink:
                return(path+[v])
            else:
                queue.append((v, path + [v]))
    return(visited)

def FordFulkerson(G_f,G,source,sink):
    path=bfs(G_f,source,sink)
    while sink in path:
        bottleneck=min([G_f[path[ii]][path[ii+1]]['vol'] for ii in range(len(path)-1)])
        [(path[ii],path[ii+1],G_f[path[ii]][path[ii+1]]['vol']) for ii in range(len(path)-1)]
        for ii in range(len(path)-1):
            G_f[path[ii]][path[ii+1]]['vol']-=bottleneck
            if G_f[path[ii]][path[ii+1]]['vol']==0:
                G_f.remove_edge(path[ii],path[ii+1])
            G_f[path[ii+1]][path[ii]]['vol']+=bottleneck
        path=bfs(G_f,source,sink)
    V1=set(bfs(G_f,source,sink))
    V2=(set([s1 for s1,s2 in G.edges])|set([s2 for s1,s2 in G.edges]))-V1
    return(V1,V2)

def getFlow(G,source,sink,period='m_vol'):
    G_f=genDiGraph(G,period)
    V1,V2=FordFulkerson(G_f,G,source,sink)
    acc=0
    for s1 in V1:
        for s2 in V2:
            if (s1,s2) in G.edges:
                acc+=G[s1][s2][period]
    return(acc)