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

## <--  Required for full functionality --> 
#ppm.bootstrapVolume()

## <--  Required for full functionality --> 
ppm.bootstrapLatency()

#snapshot_times=[]#['1667361720','1667361840']
#df,snapshots=ppm.priceEngine('FTT',datetime.date(2022,11,4),snapshot_times,240,120)
#ss=ppm.principalPathDailyBreakdown(df)
#ss.sort_values(['vol'])     