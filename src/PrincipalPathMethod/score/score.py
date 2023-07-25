import numpy as np
import pandas as pd
import datetime

from ..utils import *
from ..ppmGlobal import *

#########################################################################################
# Score  paths using the PPM method, 

def score(paths,flow,half_life=300,level_bump=120):
    # costs is the list of bottleneck costs of maximal paths
    # flow is the network flow from asset to USD
    scores={}
    # Half Life is the time in seconds for the score to decay by half, thus 600 impies a half life of ten minutes
    #print(half_life)
    kappa=np.log(2)/half_life
    max_score=-1
    max_level=1
    max_cost=(0,0,0,0,0)
    for cost in paths.keys():
        beta,bes,m_vol,lat,d_vol=cost
        #print([ex for ccy,ex in paths[cost]])
        level=min(len([ex for ccy,ex in paths[cost]]),3)-1 # level has values 1 or 2
        assert level in [1,2], 'level incorrect'
        assert beta<=0, 'beta>0'
        assert lat<=0, 'lat>0'

        sscore=np.exp(kappa*(-1*level_bump*(level-1)+beta))*float(bes)*(float(m_vol)/flow)*np.exp(kappa*lat)
        scores[(beta,bes,m_vol,lat,d_vol)]=sscore
        if sscore>max_score:
            max_score=sscore
            max_cost=(beta,bes,m_vol,lat,d_vol)
            max_level=level
    return(scores,max_score,max_cost,max_level)


