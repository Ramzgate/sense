from .utils import *

#main_path='/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/'
exchangeMap={'kraken':'KRA','coinbase':'CB','binance':'BNB','bitstamp':'BTS'}
eMap={'BINANCE':'BNB','BITSTAMP':"BTS",'COINBASE':'CB','FTX':'FTX','FTXUS':'FTXUS','KRAKEN':'KRA'}

# Decay parameter
half_life=300 

# Base Exchange Score
BES={'CB':89.32,'KRA':83.21,'BNB':36.893,'BTS':66.05,'FTX':51.21,'FTXUS':71.45,'source':1e6,'sink':1e6}
#BES={'CB':89.32,'KRA':83.21,'BNB':59.46,'BTS':66.05,'source':1e6,'sink':1e6}

##  NEEDS TO BE MOVED, CANNOT BE USED BEFORE INITALIZATION
# Keep a table with monthly data for volume for a pair on an exchange
monthlyVolume=getMonthlyVol()
#monthlyVolume[('MANA','ETH','BNB')]

CrossExchageLatency=genCrossExchageLatencyTable()


