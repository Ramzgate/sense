import os
import sys
import datetime
import json

from timeit import default_timer as timer

sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
import PrincipalPathMethod as ppm


def getMonthlyVol():
    global path_ob
    eMap={'BINANCE':'BNB','BITSTAMP':"BTS",'COINBASE':'CB','FTX':'FTX','FTXUS':'FTXUS','KRAKEN':'KRA'}
    #print(path_ob.data,path_ob.cache)
    vol=ppm.loadJsonUtility('vol.json',ppm.path_ob.cache)
    mmV={tt:sum([vol[dd][tt] for dd in vol if tt in vol[dd]])\
                for tt in set().union(*[set(vol[dd].keys()) for dd in vol])}
    monthlyVolume={(ccy1,ccy2,eMap[ex]):mmV['_'.join([ex,ccy1,ccy2])]\
                   for (ex,ccy1,ccy2) in [tuple(ww.split('_')) for ww in mmV.keys()]}
    return(monthlyVolume)

getMonthlyVol()