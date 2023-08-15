import numpy as np
import pandas as pd
import datetime

from ..utils import *
from ..ppmGlobal import *
from ..score import *

#########################################################################
# Note that all the mentions of 'path' in this file refers to paths in
# the graph and NOT in the file system
#########################################################################


#########################################################################
# Prices all the maximal paths from sink to source to obtain the price of
# the source asset denominated in the sink asset
#########################################################################

def computePathPrice(path,epoch_data):
    #print('-->',path,epoch_data,'\n')
    price=1 
    for ii in range(len(path)-1):
        zz=list(zip(path[ii],path[ii+1]))
        pp0=zz[0][0]+'/'+zz[0][1]  ;  ex0=zz[1][0]
        pp1=zz[0][1]+'/'+zz[0][0]  ;  ex1=zz[1][1]
        #print(pp0,pp1,ex0,ex1)
        if pp0 in epoch_data.keys() and ex0 in epoch_data[pp0]:
            price=price*float(epoch_data[pp0][ex0]['price'])
        elif pp1 in epoch_data.keys() and ex0 in epoch_data[pp1]:
            price=price/float(epoch_data[pp1][ex0]['price'])
    return(price)


def computeDayPrices(m_flow,daily_paths,data,snapshot_times=[],half_life=300,level_bump=120):
    snapshots={}
    ll=[]
    for epoch in daily_paths:
        timestamp=epoch['timestamp']
        epoch_costs=set([(chain['beta'],chain['bes'],chain['m_vol'],chain['latency'],chain['d_vol'])for chain in epoch['chains']])
        epoch_paths={(chain['beta'],chain['bes'],chain['m_vol'],chain['latency'],chain['d_vol']):[(link['ccy'],link['exchange'])\
                                                                 for link in chain['path']] for chain in epoch['chains']}
        
        assert epoch_costs==set(epoch_paths), 'epoch costs differnt from epoch_paths.keys()'
        
        epoch_scores,principal_score,principal_cost,principal_level=score(epoch_paths,m_flow,half_life,level_bump)

        #print('-->',epoch,'@@@',epoch_paths.keys())
        #print('-->',timestamp,data[timestamp])
        epoch_prices={cost:computePathPrice(epoch_paths[cost],data[timestamp]) for cost in epoch_paths.keys()}
                
        principal_path=epoch_paths[principal_cost]

        price=computePathPrice(principal_path,data[timestamp])
        assert epoch_prices[principal_cost]==price, 'price mismatch with epoch prices'

        gap=1e4*(max(epoch_prices.values())-min(epoch_prices.values()))/price
        #gap=1e4*(price-min(epoch_prices.values()))/price
        #gap=1e4*(max(epoch_prices.values())-price)/price

        if timestamp in snapshot_times:
            snapshots[timestamp]=(epoch_prices,epoch_scores,epoch_paths)

        ll.append({'timestamp':timestamp,\
                'price':price,\
                'path_vol':principal_cost[4]/1e6,\
                'pr_length':len(principal_path),\
                'pr_level':principal_level,\
                'lengths':[len(path) for path in list(epoch_paths.values())],\
                'gap':gap,\
                'pr_path':'->'.join([ccy for ccy,ex in principal_path]),\
                'pr_exch':'->'.join([ex for ccy,ex in principal_path])\
              })
    df=pd.DataFrame(ll)
    df.index=pd.Series([datetime.datetime.fromtimestamp(float(tt), tz = None) for tt in list(df['timestamp'])])
    return(df,snapshots)


def priceEngine(asset,current_date,snapshot_times=[],half_life=300,level_bump=120):
    # daily_paths is a list of all paths throughout the day, for each epoch/timestamp there is a list of maximal 
    # paths/chains relative to the partial order of the epoch
    m_flow,daily_paths=readDailyPaths(asset,current_date)

    #The daily data is required to extract price data for the daily paths
    daily_data=readDailyData(current_date)

    df,snapshots=computeDayPrices(m_flow,daily_paths,daily_data,snapshot_times,half_life,level_bump)
    return(df,{'snapshots':snapshots,'flow':m_flow})
