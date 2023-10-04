import os
import sys
import datetime
import json

from timeit import default_timer as timer

path2repository='/home/eyal/Research/Rutgers/PrincipalPath/'
path2config='/home/eyal/Research/Rutgers/PrincipalPath/'



sys.path.append(path2repository+'sense/src')
import PrincipalPathMethod as ppm

path_ob=ppm.Path()
path_ob.Init(path2config)

print('done')