import numpy as np
import pandas as pd
import os
import datetime
import json

from timeit import default_timer as timer

from ..classes import *
from ..utils import *
from .volume import *
from ..ppmGlobal import *

#  Add two more fields, 'bes' and 'vol', to the latency data  
# def augment(res,vol,bes):
#     #res=copy.deepcopy(res0)
#     for tt in res.keys():
#         res[tt]['vol']=vol
#         # 'bes' should be removed, as BES is a quarterly updated factor, and should not be part of daily data
#         res[tt]['bes']=bes   
#     return(res)

#  Rearrange  data from CCY-EX-Timestamp to Timestamp-CCY-EX
#  If an asset on an exchange does not have a price (aka, no trades over the last minute) assign a 'None'
# def rearrange(start,data):
#     times=[(start+ii*datetime.timedelta(0,60)).strftime('%s') for ii in range(1440)]
#     ll={}
#     for tt in times:
#         ll1={}
#         for pp in data.keys():
#             ll0={}
#             for ex in list(data[pp].keys()):
#                 if tt in data[pp][ex]:
#                     ll0[ex]=data[pp][ex][tt]
#                 else:
#                     ll0[ex]=None
#             ll1[pp]=ll0
#         ll[tt]=ll1
#     return(ll)


# revMap={'CB':'coinbase','BNB':'binance','KRA':'kraken','BTS':'bitstamp'}

# def getLatencyPrice(date):
#     mdate=''.join((date-datetime.timedelta(1)).date().__str__().split('-'))
#     ddate=''.join(date.date().__str__().split('-'))
#     print(ddate)
#     volTbl=pd.read_csv('volume/VOLUME_'+ddate+'.csv')[['ccy1','ccy2','exchange','vol']]
#     ccy_pairs=set(zip(list(volTbl[['ccy1','ccy2']]['ccy1']),list(volTbl[['ccy1','ccy2']]['ccy2'])))
#     tbl={}
#     for ccy1,ccy2 in set(ccy_pairs):
#         ll={}
#         tmpTbl=volTbl[(volTbl['ccy1']==ccy1)&(volTbl['ccy2']==ccy2)]
#         for ii in tmpTbl.exchange.index:
#             df0=dailyTransactions(ccy1,ccy2,mdate,revMap[tmpTbl['exchange'][ii]])
#             df1=dailyTransactions(ccy1,ccy2,ddate,revMap[tmpTbl['exchange'][ii]])
#             df=pd.concat([df0,df1])
#             #print(ccy1,ccy2,tmpTbl['exchange'][ii],tmpTbl['vol'][ii],len(df))
#             res0=getLatency(df,'1Min')
#             res0=res0[res0.index>=date]
#             mytimes=[tt.strftime('%s') for tt in res0.index].copy()
#             res1=pd.DataFrame(res0,copy=True)
#             res1.index=pd.Series(mytimes,index=res0.index)
#             res1=json.loads(res1.to_json(orient="index"))
#             ll[tmpTbl['exchange'][ii]]=augment(res1,tmpTbl['vol'][ii],BES[tmpTbl['exchange'][ii]]) #BES should be removed see above
#         tbl[ccy1+'/'+ccy2]=ll
#     #with open('json/'+ddate+'.json', "w") as outfile:
#     #    json.dump(tbl,outfile)
#     ttbl=rearrange(date,tbl)
#     with open('json/'+ddate+'.json', "w") as outfile:
#         json.dump(ttbl,outfile,indent=2)
#     return


def getLatency(df1,freq='1Min'):
    df2=pd.DataFrame(list(df1.index),index=df1.index,columns=['ttime']).drop_duplicates()
    # drop_duplicates() is required to remove multiple designation of the same transaction, 
    # this happens when an order runs the book through several bids/asks placed 
    # by seperate bidders
    res=df2.resample(freq).last().fillna(method="ffill").shift(periods=1)
    df3=pd.DataFrame([list(res.index),list(res['ttime'])],columns=res.index,index=['time','ttime']).T
    diff=(df3['time']-df3['ttime'])
    pp=df1[['price']].resample(freq).last().fillna(method="ffill").shift(periods=1)['price']
    ans=pd.DataFrame([list(pp),[tt.total_seconds() for tt in list(diff)]],columns=list(diff.index),index=['price','latency']).T
    return(ans)


def epochData(dd,ex0,ex1,ex2,ccy1,ccy2,ts):
    date=str2datetime(dd)
    df0=dailyTransactions(prevDay(dd),ex0,ex1,ex2,ccy1,ccy2)
    df1=dailyTransactions(dd,ex0,ex1,ex2,ccy1,ccy2)
    df2=dailyTransactions(procDay(dd),ex0,ex1,ex2,ccy1,ccy2)
    df=pd.concat([df0,df1,df2])

    res0=getLatency(df,'1Min')
    res0=res0[(res0.index>=datetime.datetime.combine(date,datetime.time(0,0,0))) & \
             (res0.index<=datetime.datetime.combine(date,datetime.time(23,59,59)))]
    #mytimes=[tt.strftime('%s') for tt in res0.index].copy()
    res1=pd.DataFrame(res0,copy=True)
    res1.index=pd.Series(ts,index=res0.index)
    res1=json.loads(res1.to_json(orient="index"))

    mvol=monthlyVolume[ccy1,ccy2,eMap[ex2]]
    bes=BES[eMap[ex2]]
    for dd in sorted(res1.keys()):
        res1[dd]['vol']=mvol
        res1[dd]['bes']=bes
    return(res1)


def genEdgeData(dd,monthlyVolume,pairMap):
    #exchangeMap={'BINANCE':'BNB','BITSTAMP':"BTS",'COINBASE':'CB','FTX':'FTX','FTXUS':'FTXUS','KRAKEN':'KRA'}
    timer_start=timer()
    date=str2datetime(dd)
    start=datetime.datetime.combine(date,datetime.time(0,0,0))
    delta=datetime.timedelta(0,60)
    ts=[(start+ii*delta).strftime('%s') for ii in range(1440)]
    print(pairMap[dd])
    print('mark 1')
    ll={} ; pairs=set([]) ; exchanges=set([])
    for pp in sorted(monthlyVolume.keys()):
        p0='_'.join(pp)
        print(pp,p0,p0 in pairMap[dd])
        if p0 in pairMap[dd]:
            (ex0,ex1,ex2,ccy1,ccy2)=pairMap[dd][p0]
            cc=ccy1+'/'+ccy2
            pairs.add(cc)  ;  exchanges.add(eMap[ex2])
            if not cc in ll:
                ll[cc]={}
            tmp_timer0=timer()
            ll[cc][eMap[ex2]]=epochData(dd,ex0,ex1,ex2,ccy1,ccy2,ts)
            print(timer()-tmp_timer0)
            assert len(ll[cc][eMap[ex2]].keys())==1440,'missing data'

    print('mark 2')
    nll={tt:{cc:{} for cc in pairs} for tt in ts}
    for tt in ts:
        for cc in pairs:
            for ex in exchanges:
                if cc in ll and ex in ll[cc]:
                    nll[tt][cc][ex]=ll[cc][ex][tt]

    print(dd,'Time:',timer(),timer_start,(timer()-timer_start)/60)
    return(nll)


def bootstrapLatency():
    #vol=loadJsonUtility('vol.json',path_ob.cache)
    pairs,usd_pairs,asset_pairs,bearing_assets=getPairs()
    for dd in ['20221102','20221103','20221104','20221105','20221106','20221107','20221108',\
               '20221109','20221110','20221111','20221112','20221113','20221114','20221115',\
                '20221116','20221117','20221118','20221119','20221120','20221121',\
                '20221122','20221123','20221124','20221125','20221126','20221127',\
                '20221128','20221129'][9:]:
        print(dd)
        pairMap={dd:{'_'.join([ccy1,ccy2,eMap[ex2]]):(ex0,ex1,ex2,ccy1,ccy2)\
                    for (ex0,ex1,ex2,ccy1,ccy2) in\
                    set(pairs[prevDay(dd)])&set(pairs[dd])&set(pairs[procDay(dd)])}\
                for dd in sorted(pairs.keys())[1:-1]}
        #monthlyVolume={tt:sum([vol[dd][tt] for dd in vol if tt in vol[dd]])\
        #            for tt in set().union(*[set(vol[dd].keys()) for dd in vol])}
        print(monthlyVolume.keys())
        res=genEdgeData(dd,monthlyVolume,pairMap)
        saveJsonUtility(res,dd+'.json',path_ob.cache+'edges/')

