import numpy as np
import pandas as pd
import os
import sys
import datetime

import networkx as nx

import copy
import json

sys.path.append('/home/eyal/Research/Rutgers/PrincipalPath/sense/src')
#sys.path.append('/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/sense/src')
import PrincipalPathMethod as ppm

snapshot_times=['1667366880','1667374800']
df,snapshots=ppm.priceEngine('MANA',datetime.date(2022,11,2),snapshot_times,360,120)
ppm.showSnapshots(snapshots)

ss=ppm.principalPathDailyBreakdown(df)
ss.sort_values(['vol'])

df[['price']].plot(subplots=True, sharey=False ,figsize=(10,4))