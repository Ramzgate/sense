import os
import sys
import datetime
import json

from timeit import default_timer as timer

#sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm


start=timer()

print('Bootstrap step 0')
start=timer()

# setp 1: Update volume table for bearing assets priced by USD or USDC
ppm.usdPairsUpdate()
print('Bootstrap step 1',timer()-start)

# step 2: find for each bearing asset dominant exchange by USD volume 
vtbl=ppm.findDominantExchanges()
print('Bootstrap step 2',timer()-start)

# step 3: update succinct price table
pjson=ppm.loadJsonUtility('price.json',ppm.path_ob.cache)
print('Bootstrap step 3.1',timer()-start)
#ptbl=ppm.priceTable2Pandas(pjson)
ptbl=ppm.priceTable2Pandas({})
print('Bootstrap step 3.2',timer()-start)
print(len(ptbl))
ptbl=ppm.updatePriceTable(ptbl,vtbl.keys(),vtbl)
print(len(ptbl))

