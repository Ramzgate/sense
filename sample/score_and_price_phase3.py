import numpy as np
import pandas as pd
import os
import sys
import datetime
import time

import networkx as nx

import copy
import json

import matplotlib.pyplot as plt
import graphviz
from graphviz import Digraph

sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
#sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm

#snapshot_times=['1667366880','1667374800']
#df,snapshots=ppm.priceEngine('FTT',datetime.date(2022,11,8),snapshot_times,360,120)
#ppm.showSnapshots(snapshots)

def periodicData(asset,start_date=datetime.date(2022,11,2),end_date=datetime.date(2022,11,30)\
                 ,half_life=240,level_bump=120):
    duration=(end_date-start_date).days
    delta=datetime.timedelta(1)
    lst=[]
    for ii in range(duration):  
        date=start_date+delta*ii
        dft,snapshots=ppm.priceEngine(asset,date,[],half_life,level_bump)
        lst.append(dft)
    df=pd.concat(lst,ignore_index=False)
    return(df)

def snapShots(asset,date,snapshot_times,half_life=240,level_bump=120):
    df,snapshots=ppm.priceEngine(asset,date,snapshot_times,half_life,level_bump)
    return(df,snapshots)





#df1,snapshots=ppm.priceEngine(asset,datetime.date(2022,11,7),snapshot_times,360,120)
#ss=ppm.principalPathDailyBreakdown(df)
#ss.sort_values(['vol'])
#print(df.keys())

if 1==2:
    df_APE=periodicData('APE',datetime.date(2022,11,2),datetime.date(2022,11,20))
    df_APE[['price']].plot(subplots=True, sharey=False ,figsize=(10,4))
    df_APE[['gap']].plot(subplots=True, sharey=False ,figsize=(10,4))

    df_FTT=periodicData('FTT',datetime.date(2022,11,2),datetime.date(2022,11,20))
    df_FTT[['price']].plot(subplots=True, sharey=False ,figsize=(10,4))
    df_FTT[['gap']].plot(subplots=True, sharey=False ,figsize=(10,4))

    df_ETH=periodicData('ETH',datetime.date(2022,11,2),datetime.date(2022,11,20))
    df_ETH[['price']].plot(subplots=True, sharey=False ,figsize=(10,4))
    plt.show()


#fig, axs = plt.subplots(2, 1)
#axs[0].plot(df.index,df['price'])
#axs[0].set_xlim(0, 2)
#axs[0].set_xlabel('Time')
#axs[0].set_ylabel('s1 and s2')
#axs[0].grid(True)

#cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
#axs[1].set_ylabel('Coherence')

#fig.tight_layout()
#plt.show()


#ppm.showSnapshots(snapshots)
#for kk in paths.keys():
#    print(kk,paths[kk])

# scrpt='digraph G {\n'
# for kk in paths:
#     ll=paths[kk]
#     ll0=["{0}/{1}".format(xx[0],xx[1]) for xx in ll]
#     scrpt+='"{0}/wallet" -> "{1}";\n'.format(asset,ll0[0])
#     for ii in range(len(ll0)-2):
#         scrpt+='"{0}" -> "{1}";\n'.format(ll0[ii],ll0[ii+1])
#     scrpt+='"{0}" -> "USD" [label="off-ramp"];\n'.format(ll0[-1])
# scrpt+='}\n'
# print(scrpt)

def generateGraph(file_name,paths,max_tuples):
    G=Digraph(file_name)
    G.attr(rankdir='LR')
    G.node("USD")
    E=[]
    for kk in paths:
        if kk in max_tuples:
            mycolor='red'
        else:
            mycolor='black'
        e=("{0}/wallet".format(asset),"{0}/{1}".format(paths[kk][0][0],paths[kk][0][1]),mycolor)
        if not e in E or e[2]=='red':
            E.append(e)
            #G.edge(e[0],e[1],color=e[2])
        for ii in range(len(paths[kk])-1):
            e=("{0}/{1}".format(paths[kk][ii][0],paths[kk][ii][1]),\
            "{0}/{1}".format(paths[kk][ii+1][0],paths[kk][ii+1][1]),mycolor)
            if not e in E or e[2]=='red':
                    E.append(e)
        e=("{0}/{1}".format(paths[kk][-1][0],paths[kk][-1][1]),"USD",mycolor)
        if not e in E or e[2]=='red':
            E.append(e)
            #G.edge(e[0],e[1],color=e[2])
    for e in E:
        if (e[0],e[1],'red') in E and (e[0],e[1],'black'):
            if e[2]=='red':
                G.edge(e[0],e[1],color='red')
        else:
            G.edge(e[0],e[1],color='black')
    G.render(file_name,format='png',directory=ppm.path_ob.cache+'/graphs')
    return

asset='FTT'
df,snapshots=snapShots(asset,datetime.date(2022,11,8),\
#                       ['1668261720','1668286740','1668306780'])
                       ['1667909760','1667913300','1667933640','1667942100',\
                        '1667953440','1667953500','1667953560','1667953620'])
timestamps=[int(time.mktime(tt.timetuple())) for tt in list(df.index)]
price=dict(zip(timestamps,list(df['price'])))
print(json.dumps(price,indent=2))

for timestamp in snapshots['snapshots']:
    myprices,myscores,mypaths=snapshots['snapshots'][timestamp]
    max_score=max([myscores[kk] for kk in myscores])
    max_tuples=[kk for kk in myscores if myscores[kk]==max_score]
    file_name=asset+'_'+timestamp
    generateGraph(file_name,mypaths,max_tuples)


