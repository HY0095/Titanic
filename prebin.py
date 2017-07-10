import numpy as np
import xlsxwriter
import time
import codecs
import pandas as pd
import math as math
import matplotlib.pyplot as plt
from scipy import stats
# %matplotlib inline
from IPython.display import SVG, HTML

_prebin_params_doc = """
    Parameters
    ----------
    y: array-like
        The dependent variable, dim = n*1
    x: array-like
        The independnet variable, dim = n*p
    method: ['quantile', 'bucket']
        The default value is 'quantile'
    binnum: int
        binnum = 20 (default)
    groupnum: int
        groupnum = 4 (default)
    """
_prebin_Result_docs = """
    role: array
        Variables'roles: 1 is selected & 0 is out
    """ 
# Interactive Grouping
class prebin(object):
    __doc__="""
    The Prebin Process
    %(Params_doc)s
    %(Result_doc)s
    Notes
    ----
    """%{"Params_doc":_prebin_params_doc,
         "Result_doc":_prebin_Result_docs}
    
    def __init__(self,data,xname,yname,**kwargs):
        self.data  = data
        self.yname = yname
        self.xname = xname
        self.xvalue = data[xname]
        self.yvalue = data[yname]
        self.binnum = 20
        
        if 'binnum' in kwargs.keys():
            self.binnum = kwargs['binnum']
        self.method = 'quantile'
        if 'method' in kwargs.keys():
            self.method = kwargs['method']
    def binning(self):       
        string_tag = 0
        # **** Split raw_data into nandata and nonandata ****
        if "missing" in list(self.xvalue):
            nanlist = self.xvalue[self.xvalue == "missing"].index
            nandata = self.data[self.xvalue == "missing"]
            nonandata = self.data.drop(nanlist)
            try:
                nonandata[self.xname] = map(float, nonandata[self.xname])
                #print("try")
                string_tag = 0
            except ValueError:
                print("Please Check Whether "+self.xname + " is String type ?" )
                print("process 'Prebin' will take "+self.xname + " as String type !!!")
                string_tag = 1
                
            nandata.loc[:, self.xname+"_bin"] = "bin_"+str(100)
            nandata.loc[:, "cut_point"]       = "missing"
        else:
            nandata = pd.DataFrame()
            nonandata = self.data
            try:
                nonandata[self.xname] = map(float, nonandata[self.xname])
                #print("try")
                string_tag = 0
            except ValueError:
                print("Please Check Whether "+self.xname + " is String type ?" )
                print("process 'Prebin' will take "+self.xname + " as String type !!!")
                string_tag = 1

        nonandata.loc[:, self.xname+'_bin'] = nonandata[self.xname]
        nonandata.loc[:, 'cut_point']  = nonandata[self.yname]
        
        if (len(set(nonandata[self.xname][:1000])) >= self.binnum):
            if (self.method == 'quantile'):
                bincut = stats.mstats.mquantiles(nonandata[self.xname], prob=np.arange(0,1,1./self.binnum))
                print(bincut)
            elif (self.method == 'bucket'):
                minvalue = min(nonandata[self.xname])
                maxvalue = max(nonandata[self.xname])
                bincut = np.arange(minvalue, maxvalue, 1.*(maxvalue-minvalue)/self.binnum)
            else:
                print("Error Message: Wrong Prebin mehtod ! Use: 'quantile' or 'bucket' ...")
                raise SystemExit
            bincut = list(set(bincut))   # remove duplicate
            bincut.sort()            
            for i in np.arange(len(bincut)+1):
                if (i == 1):
                    nonandata.loc[nonandata[self.xname] <= bincut[i], self.xname+'_bin']= 'bin_'+str(100+i)                  
                    nonandata.loc[nonandata[self.xname] <= bincut[i], 'cut_point']= bincut[i]
                elif (i>1 and i<len(bincut)):
                    nonandata.loc[(nonandata[self.xname] > bincut[i-1])&(nonandata[self.xname]<=bincut[i]), self.xname+'_bin'] = 'bin_'+str(100+i) 
                    nonandata.loc[(nonandata[self.xname] > bincut[i-1])&(nonandata[self.xname]<=bincut[i]),'cut_point'] = bincut[i]
                elif (i == len(bincut)):
                    nonandata.loc[nonandata[self.xname] > bincut[i-1], self.xname+'_bin'] = 'bin_'+str(100+i)
                    nonandata.loc[nonandata[self.xname] > bincut[i-1], "cut_point"] = max(nonandata[self.xname])
                
        else:
            bincut = list(set(nonandata[self.xname]))
            bincut.sort()
            for i,v in enumerate(bincut):
                nonandata.loc[nonandata[self.xname] == i, self.xname+'_bin'] = 'bin_'+str(100+i+1)
                nonandata.loc[nonandata[self.xname] == bincut[i],'cut_point'] = v
            
        bincut.sort()
        
        newdata = [nandata, nonandata]
      
        return [newdata, string_tag]
