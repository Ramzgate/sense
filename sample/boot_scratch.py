import os
import sys
import datetime
import json

from timeit import default_timer as timer

#sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm


vol=ppm.getMonthlyVol()
print(vol)