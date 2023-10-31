import numpy as np
import pandas as pd
import os
import sys
import datetime

import networkx as nx

import copy
import json

import PrincipalPathMethod as ppm

duration=28
if 1==1:
    current_date=datetime.date(2022,11,2)
    delta=datetime.timedelta(1)
    for ii in range(duration):  
        date=current_date+delta*ii
        print(date)
        data=ppm.readDailyData(date)
        daily_paths=ppm.computePaths('ETH',data) # APE MANA FTT GRT AAVE FIL 
        ppm.addPaths(date,daily_paths)  