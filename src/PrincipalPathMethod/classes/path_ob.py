class Path:
    def __init__(self):
        self.main=''
        self.data=''
        self.cache=''

    def Init(self):
        self.main='/Users/eyal42/Work/Full Time/Libra/Libra Research/Post Lukka Research/Rutgers/Fair Value/Sensitivity Analysis/Data/'
        #self.main='/home/eyal/Research/Rutgers/PrincipalPath/Data/'
        self.data=self.main+'CryptoTickData/Trades/trades/'
        self.cache=self.main+'cache/'
