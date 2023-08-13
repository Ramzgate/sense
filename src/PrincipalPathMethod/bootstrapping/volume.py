import numpy as np
import pandas as pd
import os
import datetime
import json

from timeit import default_timer as timer

from ..classes import *
from ..utils import *
from ..ppmGlobal import *


## Step 1: Compute volume for bearing assets, assets used to price other assets (BTC, ETH, USDC, etc.)
def getPairsExchanges():
    # scan through directory tree spanning from  '.../trades/' and identify all pairs supported by data files
    # on this directory subtree
    # Returns 
    # 1 . pairs - dictionary type with keys as strings of date '20221006', '20221013',..., for each date a array with all 
    #      extended pairs traded on the day - [('coinbase','coinbase2','COINBASE','SHIB','USD'),...] 
    # 2. asset_pairs - a set([]) with all pairs traded at some point during period - {('FTT','ETH'),('ETH','USD'),('BUSD','USDT'),...}
    pairs={}
    asset_pairs=set([])
    with os.scandir(path_ob.data) as l0:
        tmp_l0=list(l0)
        #print('l0 -->',tmp_l0)
        for ex0 in tmp_l0:
            #print('exo.path',ex0.path)
            if ex0.is_dir():
                with os.scandir(ex0.path) as l1:
                    tmp_l1=list(l1)
                    #print('l1-->',tmp_l1)
                    for ex1 in tmp_l1:
                        if ex1.is_dir():
                            with os.scandir(ex1.path) as l2:
                                tmp_l2=list(l2)
                                #print('l2-->',tmp_l2)
                                for dt in tmp_l2:
                                    if dt.is_dir():
                                        if not dt.name in pairs:
                                            pairs[dt.name]=[]
                                        with os.scandir(dt.path) as l3:
                                            tmp_l3=list(l3)
                                            #print('l3-->',tmp_l3)
                                            for pp in tmp_l3:
                                                #print(pp.name,pp.is_file())
                                                if pp.name[:2]!='._':
                                                    ex,spt,ccy1,ccy2=pp.name.split('.')[0].split('_')
                                                    pairs[dt.name].append((ex0.name,ex1.name,ex,ccy1,ccy2))
                                                    asset_pairs.add((ccy1,ccy2))
    pairs={
            date:[(ex0,ex1,ex3,ccy1,ccy2) for (ex0,ex1,ex3,ccy1,ccy2) in pairs[date] if not ccy2 in ['EUR','GBP'] ]
            for date in pairs.keys()
            }
    return(pairs,asset_pairs)

def updateVolumeJson(vol,new_pairs,bearing_assets,ptbl={}):
    # for ccy pair on exchange triples read transaction of currency pair on the exchange and compute daily volume
    # long computation
    update_flag=False
    for date in new_pairs:
        if not date in vol.keys():
            vol[date]={}
        for (ex0,ex1,ex2,ccy1,ccy2) in new_pairs[date]:
            kk='_'.join([ex2,ccy1,ccy2])
            if not kk in vol[date]:
                pp=dailyTransactions(date,ex0,ex1,ex2,ccy1,ccy2)
                if ccy2 in ['USD','USDC']:
                    vol[date][kk]=(pp['price']*pp['base_amount']).sum()
                    update_flag=True
                elif len(ptbl)>0 and ccy2 in bearing_assets and\
                    ((ccy1!='AAVE' and ccy1!='FTT' and ccy1!='FIL' and ccy1!='APE' and ccy1!='MANA') or ccy2!='BNB'):
                    pusd=ptbl[date][ccy2]
                    mrg=pd.merge_asof(
                        pp.sort_index(),
                        pusd.sort_index(),
                        left_index=True,
                        right_index=True,
                        direction='backward')[['price_x','price_y','base_amount']]
                    vol[date][kk]=(mrg['price_x']*mrg['price_y']*mrg['base_amount']).sum()
                    update_flag=True
                if update_flag:
                    print('update',date,kk)
            #print(pair,vol[date][pair])
    return(vol,update_flag)

def myfilter(vol,pairs):
    ss1=set([]).union(*[set([(ex2,ccy1,ccy2) for (ex0,ex1,ex2,ccy1,ccy2) in pairs[dd]]) for dd in pairs])
    ss2=['_'.join([ex2,ccy1,ccy2]) for (ex2,ccy1,ccy2) in ss1]
    nvol={dd:{idx:vol[dd][idx] for idx in vol[dd] if idx in ss2} for dd in vol}
    return(nvol)

def getPairs():
    # pairs - all pairs in data
    #        - dictionary type with keys as strings of date '20221006', '20221013',..., for each date a array with all 
    #          extended pairs traded on the day - [('coinbase','coinbase2','COINBASE','SHIB','USD'),...] 
    # usd_pairs - assets traded directly against USD or USDC, dict type with string as date keys, each date is a list of extended pairs as # above
    # asset_pairs - a set([]) with all pairs traded at some point during period - {('FTT','ETH'),('ETH','USD'),('BUSD','USDT'),...}
    # bearing assets - assets that appear as ccy2, list - ['BNB', 'BTC', 'BUSD', 'ETH', 'USDC', 'USDT'] 
    pairs,asset_pairs=getPairsExchanges()
    bearing_assets=sorted(set([ccy2 for (ccy1,ccy2) in asset_pairs])-set(['USD','EUR', 'GBP']))
    usd_pairs={
        dt:[(ex0,ex1,ex3,ccy1,ccy2) for (ex0,ex1,ex3,ccy1,ccy2) in pairs[dt]\
            if (ccy1 in bearing_assets and ccy2 in ['USD','USDC']) ]
            #(ccy1 in bearing_assets and ccy2 in ['USD','USDC','USDT']) ]
        for dt in pairs.keys()
        }
    return(pairs,usd_pairs,asset_pairs,bearing_assets)

def usdPairsUpdate():
    pairs,usd_pairs,asset_pairs,bearing_assets=getPairs()
    vol=loadJsonUtility('vol.json',path_ob.cache)
    vol,update_flag=updateVolumeJson(vol,usd_pairs,bearing_assets)
    saveJsonUtility(vol,'vol.json',path_ob.cache)
    # Save updated volume table as json
    # do not use date for indexing as it is not unique 
    #.set_index('date')
    #tbl.index.names = [None]
    return()

# Step 2: For each pair of assets traded  on at least one exchange,  find the most prominent exchange by volume
def findDominantExchanges():
    # upload updated volume from json and convert to pandas table
    pairs,usd_pairs,asset_pairs,bearing_assets=getPairs()
    vol=loadJsonUtility('vol.json',path_ob.cache)
    vol=myfilter(vol,usd_pairs)
    tbl=json2Table(vol)

    # adjust volume with BES score
    BES={'COINBASE':89.32,'KRAKEN':83.21,'BINANCE':36.893,'BITSTAMP':66.05,'FTX':51.21,'FTXUS':71.45}
    adj_vol=pd.Series([BES[tbl.T[ii]['exchange']]*tbl.T[ii]['vol'] for ii in tbl.index],index=tbl.index)
    bes=pd.Series([BES[tbl.T[ii]['exchange']] for ii in tbl.index],index=tbl.index)
    tbl['bes']=pd.Series([BES[tbl.T[ii]['exchange']] for ii in tbl.index],index=tbl.index)
    tbl['adjust']=pd.Series([BES[tbl.T[ii]['exchange']]*tbl.T[ii]['vol'] for ii in tbl.index],index=tbl.index)

    # find for each asset on a given day the exchange with greatest volume which will be used for pricing the asset
    idx=tbl.groupby(['date','ccy1'])['adjust'].transform(max)==tbl['adjust']
    vv=tbl[idx].groupby(['date','ccy1']).first()[['exchange','ccy2']]

    # create a table that would map for each bearing asset on a given day to path to data file used to  
    # generate a succint price history for the asset
    dates=[strDate(dd) for (dd,ccy) in list(vv.index)]
    assets=[ccy for (dd,ccy) in list(vv.index)]
    vtbl=dict(zip(dates,[dict() for dd in dates]))
    for (dd,ccy) in list(vv.index):
        vtbl[strDate(dd)][ccy]=[(ex0,ex1,ex2,ccy1,ccy2) for (ex0,ex1,ex2,ccy1,ccy2) in usd_pairs[strDate(dd)]\
                        if (ex2,ccy1,ccy2)==(vv['exchange'][(dd,ccy)],ccy,vv['ccy2'][(dd,ccy)])][0]
    return(vtbl)

# Step 3: Creat a table of succint histories for pricing other assets
def genTimeFrame(date,freq=10):
    start_date=datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
    start_time=datetime.time(0,0,0)
    start=datetime.datetime.combine(start_date,start_time)
    delta=datetime.timedelta(0,freq)
    NN=int(24*60*60/freq)
    assert NN>24, 'insufficient sampling'
    ts=[start+ii*delta for ii in range(NN)]
    return(pd.DataFrame([None]*NN,index=ts,columns=['pprice']))

def getIntervalPrice(ddate,cc,dts):
    # Get asset latest price for fixed intervals, default 10sec
    #print('--->',ddate,type(ddate))
    (ex0,ex1,ex2,ccy1,ccy2)=cc
    df=dailyTransactions(strDate(ddate),ex0,ex1,ex2,ccy1,ccy2)
    pusd=pd.merge_asof(
        dts.sort_index(),
        df[['price']].sort_index(),
        left_index=True,
        right_index=True,
        direction='backward').fillna(method='backfill')[['price']]
    return(pusd)

def updatePriceTable(ptbl,dates,vtbl):
    for dd in dates:
        if dd not in ptbl:
            ptbl[dd]=dict()
        dts=genTimeFrame(dd,freq=10)
        for ccy in vtbl[dd]:
            if ccy not in ptbl[dd]:
                print('Update!!',dd)
                ptbl[dd][ccy]=getIntervalPrice(str2datetime(dd),vtbl[dd][ccy],dts)
    return(ptbl)

def priceTable2Json(ptbl):
    pjson={}
    for dd in ptbl:
        pjson[dd]={}
        for ccy in ptbl[dd]:
            pjson[dd][ccy]={tt.__str__():ptbl[dd][ccy]['price'][tt] for tt in ptbl[dd][ccy].index}
    return(pjson)

def priceTable2Pandas(pjson):
    ptbl={}
    for dd in pjson:
        ddate=datetime.date(int(dd[:4]),int(dd[4:6]),int(dd[6:]))
        ptbl[dd]={}
        for ccy in pjson[dd]:
            ptbl[dd][ccy]=pd.DataFrame(pjson[dd][ccy],index=['price']).T
            ptbl[dd][ccy].index=sorted([datetime.datetime.strptime(tt, '%Y-%m-%d %H:%M:%S')\
                                           for tt in list(ptbl[dd][ccy].index)])
    return(ptbl)

# Step 4: compute the volume of all pairs in the DB valued in USD

def bootstrapVolume():
    print('Bootstrap step 0')
    start=timer()

    # setp 1: Update volume table for bearing assets priced by USD or USDC
    usdPairsUpdate()
    print('Bootstrap step 1',timer()-start)

    # step 2: find for each bearing asset dominant exchange by USD volume 
    vtbl=findDominantExchanges()
    print('Bootstrap step 2',timer()-start)

    # step 3: update succinct price table
    pjson=loadJsonUtility('price.json',path_ob.cache)
    print('Bootstrap step 3.1',timer()-start)
    ptbl=priceTable2Pandas(pjson)
    print('Bootstrap step 3.2',timer()-start)
    ptbl=updatePriceTable(ptbl,vtbl.keys(),vtbl)
    print('Bootstrap step 3.3',timer()-start)
    saveJsonUtility(priceTable2Json(ptbl),'price.json',path_ob.cache)
    print('Bootstrap step 3.4',timer()-start)

    # step 4: load volume table and succinct price table
    pairs,usd_pairs,asset_pairs,bearing_assets=getPairs()
    pjson=loadJsonUtility('price.json',path_ob.cache)
    ########################################################################
    ### There should be a pandas library for this that is much faster  ####
    ptbl=priceTable2Pandas(pjson)
    ########################################################################
    vol=loadJsonUtility('vol.json',path_ob.cache)
    print('Bootstrap step 4',timer()-start)

    # step 5: day by day update volume table for all assets pricing in USD through bearing assets 
    for dd in [ww for ww in sorted(set(pairs.keys())&set(ptbl.keys())) if ww>'20221031']:
        vol,update_flag=updateVolumeJson(vol,{dd:pairs[dd]},bearing_assets,ptbl)
        if update_flag:
            print('Updating',dd)
        else:
            print('No Updates',dd)
        saveJsonUtility(vol,'vol.json',path_ob.cache)
    print('Bootstrap step 5',timer()-start)
    return()
