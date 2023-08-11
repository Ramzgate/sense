import os
import sys
import datetime
import json

from timeit import default_timer as timer

#sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm


start=timer()

print('Bootstrap step 3.1',timer()-start)
pjson=ppm.loadJsonUtility('price.json',ppm.path_ob.cache)
print('Bootstrap step 3.1',timer()-start)
ptbl=ppm.priceTable2Pandas(pjson)
print('Bootstrap step 3.2',timer()-start)
print(ptbl)