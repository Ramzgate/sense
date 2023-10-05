import os
import datetime
import json


class Path:
    def __init__(self):
        self.data='xx'
        self.cache=''
        self.repository=''

    def _str_(self):
        return('\n'.join([self.data,self.cache,self.repository]))

    def Init(self):
        path=os.getenv('PPM_CNFG')
        if 'config.json' in [ff.name for ff in os.scandir(path)]:
            f=open(path+'/config.json',"r")
            pkg_paths=json.loads(f.read())
            f.close()
        else:
            raise IOError("Invalid or Empty config")

        self.data=pkg_paths['trades']
        self.cache=pkg_paths['cache']
        self.repository=pkg_paths['repository']

