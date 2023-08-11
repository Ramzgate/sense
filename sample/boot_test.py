import os
import sys
import datetime
import json

from timeit import default_timer as timer

sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
import PrincipalPathMethod as ppm

pairs=ppm.getPairsExchanges()
print(pairs)