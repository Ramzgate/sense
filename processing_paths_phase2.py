import numpy as np
import pandas as pd
import os
import datetime

import networkx as nx

import copy
import json

import PrincipalPathMethod as ppm

duration=1
if 1==1:
    current_date=datetime.date(2022,11,29)
    delta=datetime.timedelta(1)
    for ii in range(duration):
        date=current_date+delta*ii
        print(date)
        data=ppm.readDailyData(date)
        daily_paths=ppm.computePaths('MANA',data)
        ppm.addPaths(date,daily_paths)