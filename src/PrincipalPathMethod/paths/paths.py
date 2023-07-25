import numpy as np
import pandas as pd
import datetime
import networkx as nx

from ..utils import *
from ..ppmGlobal import *
from ..flow import *


def getCrossExchangePairs(epoch_data):
    exSupp={}
    for exchange in ['BNB','CB','BTS','KRA','FTX','FTXUS']:
        exSupp[exchange]=set([pp.split('/')[0] for pp in epoch_data.keys() if exchange in (epoch_data[pp]).keys() ])|\
        set([pp.split('/')[1] for pp in epoch_data.keys() if exchange in (epoch_data[pp]).keys() ])
    ll=set([])
    for exchange1 in ['BNB','CB','BTS','KRA']:
        for exchange2 in set(['BNB','CB','BTS','KRA','FTX','FTXUS'])-set([exchange1]):
            for ccy in exSupp[exchange1]&exSupp[exchange2]:
                ll.add(((ccy,exchange1),(ccy,exchange2)))
    return(ll)

def genGraph(asset,epoch_data):
    global BES
    global monthlyVolume
    global CrossExchageLatency
    G = nx.Graph()
    for pp in epoch_data.keys():
        for ex in epoch_data[pp].keys():
            if epoch_data[pp][ex]:
                p=pp.strip().split('/')
                s1=(p[0],ex)
                s2=(p[1],ex)
                G.add_edge(s1,s2)
                G[s1][s2]['beta']=0
                #G[s1][s2]['bes']=epoch_data[pp][ex]['bes']
                G[s1][s2]['bes']=min(BES[s1[1]],BES[s2[1]])
                G[s1][s2]['m_vol']=monthlyVolume[(s1[0],s2[0],ex)]
                G[s1][s2]['latency']=-1*epoch_data[pp][ex]['latency']
                G[s1][s2]['d_vol']=epoch_data[pp][ex]['vol']

    cross_exchage=getCrossExchangePairs(epoch_data)
    for (s1,s2) in cross_exchage:
        G.add_edge(s1,s2)
        G[s1][s2]['beta']=-1*CrossExchageLatency[(s1[0],s1[1],s2[1])]
        G[s1][s2]['bes']=min(BES[s1[1]],BES[s2[1]])
        G[s1][s2]['m_vol']=1e15 
        G[s1][s2]['latency']=0
        G[s1][s2]['d_vol']=1e15 

    asset_cntr=set([s1 for (s1,s2) in G.edges if s1[0]==asset])|set([s2 for (s1,s2) in G.edges if s2[0]==asset])
    for s2 in asset_cntr:
        s1=(asset, 'source')
        G.add_edge(s1,s2)
        G[s1][s2]['beta']=0
        G[s1][s2]['bes']=min(BES[s1[1]],BES[s2[1]])
        G[s1][s2]['m_vol']=1e15 
        G[s1][s2]['latency']=0
        G[s1][s2]['d_vol']=1e15 

    USD_Cntr=set([s1 for (s1,s2) in G.edges if s1[0]=='USD'])|set([s2 for (s1,s2) in G.edges if s2[0]=='USD'])
    for s1 in USD_Cntr:
        s2=('USD', 'sink')
        G.add_edge(s1,s2)
        G[s1][s2]['beta']=0
        G[s1][s2]['bes']=min(BES[s1[1]],BES[s2[1]])
        G[s1][s2]['m_vol']=1e15 
        G[s1][s2]['latency']=0
        G[s1][s2]['d_vol']=1e15 

    # ('beta','bes','vol','latency')
    for s in G.nodes:
        G.nodes[s]['cost']=set([(0,0,0,-1e5,0)])
        G.nodes[s]['path']={(0,0,0,-1e5,0):[]}
    G.nodes[(asset,'source')]['cost']=set([(0,1e20,1e20,0,1e20)])
    G.nodes[(asset,'source')]['path']={(0,1e20,1e20,0,1e20):[(asset,'source')]}
    return(G)

def comp(x,y):
    return((sum([x[ii]>=y[ii] for ii in range(4)])==4) or (sum([x[ii]<=y[ii] for ii in range(4)])==4))
def greater(x,y):
    return((sum([x[ii]>=y[ii] for ii in range(4)])==4) and (sum([x[ii]>y[ii] for ii in range(4)])>0))
def equal(x,y):
    return(sum([x[ii]==y[ii] for ii in range(4)])==4)
def prog(v,e):
    ans=[v[0]+e[0],None,None,None,None]
    for ii in range(1,5):
        ans[ii]=min(v[ii],e[ii])
    return(tuple(ans))

def ppmBFS(graph, source, sink):
    queue= [source]
    while queue:
        #print('queue:',len(queue))
        u = queue.pop(0)
        path_length=max([len(graph.nodes[u]['path'][xx]) for xx in graph.nodes[u]['cost']])
        #print('path length:',path_length)
        neighbors = set(graph[u].keys()) - set([u])
        #print('u',u,'neighbors:',neighbors)
        for v in neighbors:
            #print(u,v,queue)
            for xx in graph.nodes[u]['cost']:
                if v in graph.nodes[u]['path'][xx]:
                    continue
                e=(graph[u][v]['beta'],graph[u][v]['bes'],graph[u][v]['m_vol'],graph[u][v]['latency'],graph[u][v]['d_vol'])
                x=prog(xx,e)
                compare_flag=False
                #print(v,graph.nodes[v]['distance'])
                for y in list(graph.nodes[v]['cost']):
                    if not comp(x,y):
                        continue
                    if greater(y,x) or equal(x,y):
                        compare_flag=True
                    if greater(x,y):
                        compare_flag=True
                        graph.nodes[v]['cost'].remove(y)
                        del graph.nodes[v]['path'][y]
                        #print(u,v,graph.nodes[u]['path'][xx])
                        graph.nodes[v]['cost'].add(x)
                        graph.nodes[v]['path'][x]=graph.nodes[u]['path'][xx]+[v]
                        queue.append(v)
                if not compare_flag:
                    graph.nodes[v]['cost'].add(x)
                    graph.nodes[v]['path'][x]=graph.nodes[u]['path'][xx]+[v]
                    queue.append(v)
    return(graph.nodes[sink]['cost'],graph.nodes[sink]['path'])

def computePaths(asset,data):
    daily_paths={}
    #date=''.join(ddate.date().__str__().split('-'))
    #data=getDailyData(date)
    costTbl={}
    timestamp0=min(data.keys())
    G=genGraph(asset,data[timestamp0])
    m_flow=getFlow(G,(asset,'source'),('USD','sink'),'m_vol')
    ll=[]
    for timestamp in list(data.keys()):#[1:100]:
        G=genGraph(asset,data[timestamp])
        costs,paths=ppmBFS(G,(asset,'source'),('USD','sink'))
        costTbl[timestamp]=(costs,paths)

        ll0=[]
        for cc in costs:
            rr=dict(zip(['beta','bes','m_vol','latency','d_vol'],cc))
            pp=[]
            for ccy,ex in paths[cc][1:-1]:
                pp.append({'ccy':ccy,'exchange':ex})
            rr['path']=pp
            ll0.append(rr)    
        ll1={'timestamp':timestamp,'chains':ll0}
        ll.append(ll1)
    daily_paths[asset]={'m_flow':m_flow,'daily_paths':ll}
    return(daily_paths)
