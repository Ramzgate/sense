import numpy as np
import pandas as pd

import os
import sys
import datetime
import json

from timeit import default_timer as timer

sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
#sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm


start=timer()

print('Bootstrap step 0')
start=timer()

# # setp 1: Update volume table for bearing assets priced by USD or USDC
# ppm.usdPairsUpdate()
# print('Bootstrap step 1',timer()-start)

# # step 2: find for each bearing asset dominant exchange by USD volume 
# vtbl=ppm.findDominantExchanges()
# print('Bootstrap step 2',timer()-start)

# step 3: update succinct price table
# pjson=ppm.loadJsonUtility('price.json',ppm.path_ob.cache)
# print('Bootstrap step 3.1',timer()-start)
# ptbl=ppm.priceTable2Pandas(pjson)
# #ptbl=ppm.priceTable2Pandas({})
# print('Bootstrap step 3.2',timer()-start)
# print(len(ptbl))
# ptbl=ppm.updatePriceTable(ptbl,vtbl.keys(),vtbl)
# print('Bootstrap step 3.3',timer()-start)
# ppm.saveJsonUtility(ppm.priceTable2Json(ptbl),'price.json',ppm.path_ob.cache)
# print('Bootstrap step 3.4',timer()-start)

# # step 4: load volume table and succinct price table
# pairs,usd_pairs,asset_pairs,bearing_assets=ppm.getPairs()
# pjson=ppm.loadJsonUtility('price.json',ppm.path_ob.cache)
# ########################################################################
# ### There should be a pandas library for this that is much faster  ####
# ptbl=ppm.priceTable2Pandas(pjson)
# ########################################################################
# vol=ppm.loadJsonUtility('vol.json',ppm.path_ob.cache)
# print('Bootstrap step 4',timer()-start)

#print(pairs['20221108'])

def updateVolumeJson(vol,new_pairs,bearing_assets,ptbl={}):
    # for ccy pair on exchange triples read transaction of currency pair on the exchange and compute daily volume
    # long computation
    update_flag=False
    for date in new_pairs:
        if not date in vol.keys():
            vol[date]={}
        for (ex0,ex1,ex2,ccy1,ccy2) in new_pairs[date]:
            kk='_'.join([ex2,ccy1,ccy2])
            print(date,kk)
            if not kk in vol[date]:
                pp=ppm.dailyTransactions(date,ex0,ex1,ex2,ccy1,ccy2)
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


# step 5: day by day update volume table for all assets pricing in USD through bearing assets 
# for dd in [ww for ww in sorted(set(pairs.keys())&set(ptbl.keys())) if ww>'20221031']:
#     vol,update_flag=updateVolumeJson(vol,{dd:pairs[dd]},bearing_assets,ptbl)
#     if update_flag:
#         print('Updating',dd)
#     else:
#         print('No Updates',dd)
#     ppm.saveJsonUtility(vol,'vol.json',ppm.path_ob.cache)

def extract_relevant_fields(df,ex2,ccy1,ccy2):
    df['pair']=pd.Series(dict(zip(df.index,[ccy1+'/'+ccy2]*df.index.size)))
    df['exchange']=pd.Series(dict(zip(df.index,[ex2]*df.index.size)))
    df0=df[['price','base_amount','taker_side','pair','exchange']]
    return(df0)

def dailyTransactions(date,ex0,ex1,ex2,ccy1,ccy2):
    full_path=ppm.path_ob.data+ex0+'/'+ex1+'/'+date+'/'+ex2+'_SPOT_'+ccy1+'_'+ccy2+'.csv.gz'
    print(full_path)
    print('1')
    #df=pd.read_csv(full_path,delimiter=';',compression='infer',
    #           parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange')
    reader=pd.read_csv(full_path,delimiter=';',compression='gzip',
                       parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange',chunksize=10**3)
    df=pd.concat([extract_relevant_fields(x,ex2,ccy1,ccy2) for x in reader],ignore_index=True)
    return(df)

start=timer()
df=dailyTransactions('20221108','binance','binance1','BINANCE','BTC','USDT')
print('Bootstrap step 1',timer()-start)

print(df.head(3))
print(df.tail(3))
print(df.size)
#full_path='/home/eyal/Research/Rutgers/PrincipalPath/Data/CryptoTickData/Trades/trades/binance/binance1/20221108/BINANCE_SPOT_BTC_USDT.csv.gz'
#df=pd.read_csv(full_path,delimiter=';',compression='infer',parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange')


#def readCSV(date,ex0,ex1,ex2,ccy1,ccy2):
#    reader=pd.read_csv(full_path,delimiter=';',compression='infer',parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange',chunksize=10**3)
#    df=pd.concat([extract_relevant_fields(x,'BINANCE','BTC','USDT') for x in reader],ignore_index=True)
#print(df.head(3))
#print(df.tail(3))