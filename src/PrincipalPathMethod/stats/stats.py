import numpy as np
import pandas as pd

import datetime


def path_string_gen(ccy_path_str,ex_path_str):
    ccys=[]  ;  trns=[]
    ccy_path=ccy_path_str.split('->')
    ex_path=ex_path_str.split('->')
    assert len(ccy_path)==len(ex_path), 'ccy exchange paths mismatch'
    for k,ccy in enumerate(ccy_path[:-1]):
        if ccy_path[k]!=ccy_path[k+1]:
            ccys.append(ccy)
        elif ex_path[k]!=ex_path[k+1]:
            trns.append([ex_path[k],ccy_path[k],ex_path[k+1]])
    ccys.append(ccy_path[-1])
    assert [ww[0] for ww in trns[1:]]==[ww[-1] for ww in trns[:-1]], 'exchange transition mismatch'
    path_str='->'.join(ccys)
    ex_str=ex_path[0]
    if trns:
        ex_str+=(''.join(['->('+ww[1]+')->'+ww[2] for ww in trns])).strip()
    return(path_str+' , '+ex_str)



def principalPathDailyBreakdown(df):
    ll=[]
    pt=set(zip(list(df['pr_path']),list(df['pr_exch'])))
    for ccy_path_str,ex_path_str in pt:
        ddf=df[(df['pr_path']==ccy_path_str)&(df['pr_exch']==ex_path_str)]
        #print('{0:30} , {1:30} , {2:4} , {3:6.4}'.format(cp,ep,len(ddf), max(ddf['path_vol'])))
        path_str=path_string_gen(ccy_path_str,ex_path_str)
        ll.append({'path':path_str,'dist':100*len(ddf)/1440,'vol':max(ddf['path_vol'])})
    return(pd.DataFrame(ll))