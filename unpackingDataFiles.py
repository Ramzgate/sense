import os
import datetime
import json
import shutil
import tarfile

path='/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/Data/Test/'

def getSucc(path):
    with os.scandir(path) as drct:
        n=max([int(ff.name.split('_')[1]) for ff in drct])+1
    exchange=path.split('/')[-1]
    return(exchange+'_'+str(n))


with os.scandir(path+'trades_compressed_test/') as drct:
    ll=[ff.name for ff in drct if 'tar' in ff.name.split('.')] 
file_lst=sorted(ll)
#print(file_lst[0])

for file in file_lst:
    if os.path.exists(path+'trades/'):
        shutil.rmtree(path+'trades/',ignore_errors=True)    

    tar = tarfile.open(path+'trades_compressed_test/'+file, 'r')
    tar.extractall()
    tar.close()

    if os.path.exists(path+'trades/20221105/'):
        with os.scandir(path+'trades/20221105/') as drct:
            ll=set([ff.name.split('_')[0] for ff in drct if 'csv' in ff.name.split('.')])
    assert len(ll)==1, 'Multiple exchanges' 
    exchange=sorted(ll)[0].lower()
    if not os.path.exists(path+exchange+'/'):
        os.mkdir(exchange)
    if not os.path.exists(path+exchange+'/'+exchange+'_0/'):
        shutil.move(path+'trades/', path+exchange+'/'+exchange+'_0/')
    else:
        next_exchange=getSucc(path+exchange+'/')
        shutil.move(path+'trades/', path+exchange+'/'+next_exchange+'_0/')



    

#shutil.move(original, target)
