import numpy as np
import pandas as pd
import os
import datetime
import json

from ..classes import Path
from ..classes import *


path_ob=Path()
path_ob.Init()

##############################################################
########################  Json Utilities  ####################
##############################################################


def loadJsonUtility(file,path):
    # <file [str] , path [str]>
    if file in [ff.name for ff in os.scandir(path)]:
        f=open(path+file,"r")
        data=json.loads(f.read())
        f.close()
    else:
        data={}
    return(data)

def saveJsonUtility(data,file,path):
    with open(path+file, "w") as outfile:
        json.dump(data,outfile,indent=2)
    return

def json2Table(vol):
    # structure the volume data in a json and dataframe
    tvol=[]
    for date in sorted(vol.keys()):
        ddate=datetime.date(int(date[:4]),int(date[4:6]),int(date[6:]))
        for idx in vol[date]:
            [ex2,ccy1,ccy2]=idx.split('_')
            tvol.append([ddate,ex2,ccy1,ccy2,vol[date][idx]])
    tbl=pd.DataFrame(tvol,columns=['date','exchange','ccy1','ccy2','vol'])
    return(tbl.sort_index())

def addPaths(date,new_paths):
    assert type(date)==type(datetime.date(2022,12,31)), 'Type error for date variable'
    ddate=datetime2str(date)
    prev_paths=loadJsonUtility(ddate+'.json',path_ob.cache+'paths/')
    prev_paths.update(new_paths)  # .update() is a dict method 
    saveJsonUtility(prev_paths,ddate+'.json',path_ob.cache+'paths/')
    return



########################################################################
########################  Daily Transaction Utilities  #################
########################################################################
##  Reads daily transaction from original source '.csv.gz' file from CryptoTick

# def dailyTransactions(date,ex0,ex1,ex2,ccy1,ccy2):
#     full_path=path_ob.data+ex0+'/'+ex1+'/'+date+'/'+ex2+'_SPOT_'+ccy1+'_'+ccy2+'.csv.gz'
#     df=pd.read_csv(full_path,delimiter=';',compression='infer',
#                parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange')
#     df['pair']=pd.Series(dict(zip(df.index,[ccy1+'/'+ccy2]*df.index.size)))
#     df['exchange']=pd.Series(dict(zip(df.index,[ex2]*df.index.size)))
#     df0=df[['price','base_amount','taker_side','pair','exchange']]
#     return(df0)

def extract_relevant_fields(df,ex2,ccy1,ccy2):
    df['pair']=pd.Series(dict(zip(df.index,[ccy1+'/'+ccy2]*df.index.size)))
    df['exchange']=pd.Series(dict(zip(df.index,[ex2]*df.index.size)))
    df0=df[['price','base_amount','taker_side','pair','exchange']]
    return(df0)

def dailyTransactions(date,ex0,ex1,ex2,ccy1,ccy2):
    print('-->')
    full_path=path_ob.data+ex0+'/'+ex1+'/'+date+'/'+ex2+'_SPOT_'+ccy1+'_'+ccy2+'.csv.gz'
    reader=pd.read_csv(full_path,delimiter=';',compression='gzip',
                       parse_dates=['time_exchange','time_coinapi'],index_col='time_exchange',chunksize=10**3)
    df=pd.concat([extract_relevant_fields(x,ex2,ccy1,ccy2) for x in reader],ignore_index=False)
    return(df)


########################################################################
########################  Monthly Volume Utilities  ####################
########################################################################
## Reads monthly volume data from cached file 'vol.json'
#
#  monthlyVolume - {('USDT','USD','FTX'):2852416873.226717,('USDT','USD','BTS'):127322350.14148754,...

def getAllDaysInMonth(month,year):
    date=datetime.date(year,month,1)
    delta=datetime.timedelta(1)
    day_lst=[]
    while date.month==month:
        day_lst.append(date)
        date=date+delta
    day_lst=set([''.join(date.__str__().split('-')) for date in sorted(day_lst)])
    return(day_lst)

def getMonthlyVol():
    global path_ob
    eMap={'BINANCE':'BNB','BITSTAMP':"BTS",'COINBASE':'CB','FTX':'FTX','FTXUS':'FTXUS','KRAKEN':'KRA'}
    month=11 ; year=2022 # this is the only month the existing DB has reliable data, for a larger DB it would make sense to average across avaialble months
    days_in_month=getAllDaysInMonth(month,year)
    vol=loadJsonUtility('vol.json',path_ob.cache)
    exchange_pairs=set().union(*[set(vol[dd].keys()) for dd in vol])  # {'BINANCE_AAVE_BNB','BINANCE_AAVE_BTC',...
    mmV={}
    for ex_pair in exchange_pairs:
        days_traded_in_month=set([date for date in vol if ex_pair in vol[date]])&days_in_month
        monthly_vol=sum([vol[date][ex_pair] for date in days_traded_in_month])
        avg_daily_vol=monthly_vol/len(days_traded_in_month)
        mmV[ex_pair]=avg_daily_vol*len(days_in_month)
        #mmV={ex_pair:sum([vol[date][ex_pair] for date in vol if ex_pair in vol[date]])  for ex_pair in exchange_pairs}
    monthlyVolume={(ccy1,ccy2,eMap[ex]):mmV['_'.join([ex,ccy1,ccy2])] for (ex,ccy1,ccy2) in [tuple(ww.split('_')) for ww in mmV.keys()]}
    return(monthlyVolume)

#############################################################
######################## Data Utilities  ####################
#############################################################


# Daily data json file format

# {
#   "1667361600": {
#     "ETH/USD": {
#       "CB": {
#         "price": 1578.24,
#         "latency": 0.151524,
#         "vol": 934976289.3519064,
#         "bes": 89.32
#       },
#       "KRA": {
#         "price": 1578.6,
#         "latency": 5.02,
#         "vol": 95343431.75235292,
#         "bes": 83.21

#       ...

# Load data from a json file as above
def readDailyData(date):
    
    assert type(date)==type(datetime.date(2022,12,31)), 'Type error for date variable'
    
    #start=datetime.datetime(int(date[:4]),int(date[4:6]),int(date[6:8]),0,0,0,0)
    start=datetime.datetime.combine(date,datetime.time(0,0,0,0))
    delta=datetime.timedelta(0,60)
    timestamps0=set([(start+ii*delta).strftime('%s') for ii in range(1440)])
    timestamps1=set([(start+ii*delta) for ii in range(1440)])

    ddate=datetime2str(date)
    #f=open('json2/'+ddate+'.json',"r")
    #data=json.loads(f.read())
    #f.close()
    data=loadJsonUtility(ddate+'.json',path_ob.cache+'edges/')

    assert timestamps0==set(data.keys()), 'missing timestamps 0'
    assert timestamps1==set([datetime.datetime.fromtimestamp(float(tt), tz = None) for tt in data.keys()]), 'missing timestamps 1'

    assert list(data.keys())[0]==start.strftime('%s'), 'Start time error'
    assert list(data.keys())[-1]==(start+1439*delta).strftime('%s'), 'End time error'
    
    return(data)


#############################################################
######################## Path Utilities  ####################
#############################################################


# Path data json file format

# {
#   "MANA": {
#     "m_flow": 533658284.23399764,
#     "daily_paths": [
#       {
#         "timestamp": "1667448000",
#         "chains": [
#           {
#             "beta": -30,
#             "bes": 35.96,
#             "m_vol": 314883797.56430995,
#             "latency": -42.637,
#             "d_vol": 9313952.4867,
#             "path": [
#               {
#                 "ccy": "MANA",
#                 "exchange": "BNB"
#               },
#               {
#                 "ccy": "USDT",
#                 "exchange": "BNB"
#               }
#             ]
            
#          ...

# Load path data from a json file as above
def readDailyPaths(asset,date):
    
    assert type(date)==type(datetime.date(2022,12,31)), 'Type error for date variable'
    
    start=datetime.datetime.combine(date,datetime.time(0,0,0,0))
    delta=datetime.timedelta(0,60)
    timestamps0=set([(start+ii*delta).strftime('%s') for ii in range(1440)])
    timestamps1=set([(start+ii*delta) for ii in range(1440)])

    ddate=''.join(date.__str__().split('-'))
    data=loadJsonUtility(ddate+'.json',path_ob.cache+'paths/')
    
    m_flow=data[asset]['m_flow']
    daily_paths=data[asset]['daily_paths']

    assert timestamps0==set([pp['timestamp'] for pp in daily_paths]), 'missing timestamps 0'

    return(m_flow,daily_paths)



#######################################################################
########################  Visualization Utilities  ####################
#######################################################################

def showSnapshots(snaps):
    flow=snaps['flow']
    snapshots=snaps['snapshots']
    print(' {6:28}  {7:28}  {0:9}  {1:8}  {2:4}  {3:7}  {4:7}  {5:3}'\
            .format('prices','scores','beta','bes','latency','rel flow','path ccys','path exchanges'))
    for timestamp in snapshots.keys():
        print(datetime.datetime.fromtimestamp(float(timestamp), tz = None),'<-->',timestamp)
        myprices,myscores,mypaths=snapshots[timestamp]
        for ss in myscores.keys():
            tccy='->'.join([ccy for ccy,ex in mypaths[ss]])
            tex='->'.join([ex for ccy,ex in mypaths[ss]])
            print(' {6:28}, {7:28}, {0:9.4f}, {1:8.3f}, {2:4.0f}, {3:7.2f}, {4:7.3f}, {5:3.1f}'\
                  .format(myprices[ss],myscores[ss],np.abs(ss[0]),ss[1],np.abs(ss[3]),100*ss[2]/flow,tccy,tex))
        print()
    return


#######################################################################
########################  Latency Kappa Utilities  ####################
#######################################################################

def cLat(ccy):
    chainLat={'CASH':2,'BTC':600,'ETH':20,'ETH_TOK':30,'ETH_ALT':25,'CRO':50,'FIL':50,'FTT':40,'ATOM':50,\
              'UST':50,'SHIB':200}
    chainType={'BTC':'BTC',\
               'ETH':'ETH',\
               'GRT':'ETH_TOK', 'MANA':'ETH_TOK', 'DAI':'ETH_TOK','BUSD':'ETH_TOK','APE':'ETH_TOK','AAVE':'ETH_TOK',\
               'USDT':'ETH_TOK', 'USDC':'ETH_TOK',\
               'BNB':'ETH_ALT',\
               'CRO':'CRO' ,'FIL':'FIL' ,'FTT':'FTT' ,'ATOM':'ATOM' ,'UST':'UST','SHIB':'SHIB',\
               'USD':'CASH'
              }
    return(chainLat[chainType[ccy]])

def exLat(ex0,ex1):
    exLoc={'BNB':'ASIA', 'BTS':'EUR', 'CB':'USA', 'FTX':'BAH', 'FTXUS':'USA', 'KRA':'USA'}
    locLat={
            ('ASIA', 'ASIA'):10,\
            ('ASIA', 'BAH'):20,\
            ('ASIA', 'EUR'):15,\
            ('ASIA', 'USA'):20,\
            ('BAH', 'ASIA'):20,\
            ('BAH', 'BAH'):5,\
            ('BAH', 'EUR'):15,\
            ('BAH', 'USA'):10,\
            ('EUR', 'ASIA'):20,\
            ('EUR', 'BAH'):15,\
            ('EUR', 'EUR'):5,\
            ('EUR', 'USA'):15,\
            ('USA', 'ASIA'):20,\
            ('USA', 'BAH'):10,\
            ('USA', 'EUR'):15,\
            ('USA', 'USA'):5\
            }
    return(locLat[(exLoc[ex0],exLoc[ex1])])

def genCrossExchageLatencyTable():
    eMap={'BINANCE':'BNB','BITSTAMP':"BTS",'COINBASE':'CB','FTX':'FTX','FTXUS':'FTXUS','KRAKEN':'KRA'}
    vol=loadJsonUtility('vol.json',path_ob.cache)
    exchanges=set([eMap[ww.split('_')[0]] for ww in set().union(*[set(vol[dd]) for dd in vol.keys()])])
    assets=set(['USD'])|set([ww.split('_')[1] for ww in set().union(*[set(vol[dd]) for dd in vol.keys()])])
    support1=set([(eMap[ww.split('_')[0]],ww.split('_')[1]) for ww in set().union(*[set(vol[dd]) for dd in vol.keys()])])
    support2=set([(eMap[ww.split('_')[0]],ww.split('_')[2]) for ww in set().union(*[set(vol[dd]) for dd in vol.keys()])])
    support=support1|support2
    exchanges_support={ex0:set([ccy for (ex,ccy) in support if ex==ex0]) for ex0 in exchanges}
    CrossExchageLatency={}
    for ccy in assets:
        for ex0 in exchanges:
            for ex1 in exchanges-set([ex0]):
                if ccy in exchanges_support[ex0]&exchanges_support[ex1]:
                    CrossExchageLatency[(ccy,ex0,ex1)]=cLat(ccy)+exLat(ex0,ex1)
    return(CrossExchageLatency)


#####################################################################
########################  Date Format Utilities  ####################
#####################################################################

def digitPadding(n):
    if len(n)==1:
        n='0'+n
    return(n)

def strDate(date):
    return(str(date.year)+digitPadding(str(date.month))+digitPadding(str(date.day)))

def datetime2str(ddate):
    return(str(ddate.year)+digitPadding(str(ddate.month))+digitPadding(str(ddate.day)))

def digitPadding(n):
    if len(n)==1:
        n='0'+n
    return(n)

def str2datetime(date):
    return(datetime.date(int(date[:4]),int(date[4:6]),int(date[6:])))

def prevDay(date):
    return(datetime2str(str2datetime(date)-datetime.timedelta(1)))

def procDay(date):
    return(datetime2str(str2datetime(date)+datetime.timedelta(1)))

