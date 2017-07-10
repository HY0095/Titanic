import prebin 
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


class grouping(object):
    
    def __init__(self, data, yname, xname, i, sqlpath, **kwargs):
        self.yname = yname
        self.xname = xname
        self.cnt   = i
        self.sqlpath = sqlpath
        self.nandata = data[0][0]
        self.data  = data[0][1]
        self.string_tag = data[1]
        self.mingroupsize = 0.05
        if 'mingroupsize' in kwargs.keys():
            self.mingroupsize = kwargs['mingroupsize']
            
    def freq(self):
        Dict     = {}
        freqs    = list()
        sumy     = {"y0":0., "y1":0.}
        var_name = list()
        ylist    = list()
        cut      = list()
        _tmpcut_ = list()
        tmpcut   = list()
        _tmpx_   = list(set(self.data[self.xname]))
        _tmpy_   = list(set(self.data[self.yname]))
        _tmpx_.sort()
        _tmpy_.sort()
        
        for name in _tmpx_:
            for y in _tmpy_:
                var_name.append(name)
                ylist.append(y)
                freqs.append(len(self.data[(self.data[self.xname] == name) & (self.data[self.yname] == y)]))
                cut.append(max(self.data.cut_point[self.data[self.xname] == name]))
            _tmpcut_.append(max(self.data.cut_point[self.data[self.xname] == name]))
            
        for k,v in enumerate(_tmpcut_):
            if (self.string_tag == 0) :
                if k > 0 :
                    tmpcut.append((_tmpcut_[k-1]+_tmpcut_[k])/2.)
            else :
                tmpcut.append(_tmpcut_[k])

        freq_table = pd.DataFrame(np.vstack((ylist,var_name,cut,freqs)).T, columns = [self.yname,self.xname,'Cut','Count'])
        if self.string_tag == 0:
            freq_table[[self.yname,'Cut','Count']] = freq_table[[self.yname,'Cut','Count']].astype(float)
        else:
            freq_table[[self.yname,'Count']] = freq_table[[self.yname,'Count']].astype(float)
            
        Dict = {"cutpoint":_tmpcut_, "binx":_tmpx_, "freqy":sumy, "freqtable":freq_table}
        return Dict
    
    def entropy(self, _tmpdata_, y, cut):
        Dict = {}
        toa  = 1.*sum(y.values())
        y_0  = y["y0"]/toa
        y_1  = y["y1"]/toa 
        x_1  = 1.*sum(_tmpdata_.Count[_tmpdata_.Cut <= cut])
        x_2  = toa - x_1
        x11  = 1.*sum(_tmpdata_.Count[(_tmpdata_.Cut <= cut) & (_tmpdata_[self.yname] == 1)])
        x10  = x_1-x11
        x21  = 1.*sum(_tmpdata_.Count[(_tmpdata_.Cut > cut) & (_tmpdata_[self.yname] == 1)])
        x20  = x_2 - x21
        entS = -y_0*np.log2(y_0) - y_1*np.log2(y_1)
        if x10 == 0:
            entx10 = 0
        else:
            entx10 = (x_1/toa)*(-(x10/x_1)*np.log2(x10/x_1))  
        if x11 == 0:
            entx11 = 0
        else:
            entx11 = (x_1/toa)*(-(x11/x_1)*np.log2(x11/x_1))
        if x20 == 0:
            entx20 = 0
        else :
            entx20 = (x_2/toa)*(-(x20/x_2)*np.log2(x20/x_2))
        if x21 == 0:
            entx21 = 0
        else:
            entx21 = (x_2/toa)*(-(x21/x_2)*np.log2(x21/x_2))  
        entx = entx10 + entx11 + entx20 + entx21
        Dict = {cut:(entS-entx)}
        return Dict
    
    def calsplit(self, predata):
        tmpdict = {}
        initvalue = 0.
        cutvalue = {}
        cutpoint = list(set(predata.Cut))
        freqy = {}
        freqy["y0"] = sum(predata.Count[predata[self.yname] == 0])
        freqy["y1"] = sum(predata.Count[predata[self.yname] == 1])
        cutpoint.sort()
        for i, value in enumerate(cutpoint):
            if i < len(cutpoint)-1:
                _binentropy_ = self.entropy(predata, freqy, value)
                if initvalue <= _binentropy_.values()[0]:
                    cutvalue = _binentropy_
                    initvalue = _binentropy_.values()[0]
                tmpdict[i] = _binentropy_
        return cutvalue.keys()[0]
    
    def split(self):
        bestgroup = {}
        cutlist   = list()
        predata   = self.freq()
        freqtable = predata['freqtable']
        total = sum(freqtable.Count)
        minsize = round(total*self.mingroupsize, 0)
        tmpdict0 = self.calsplit(freqtable)
        left0 = sum(freqtable.Count[freqtable.Cut <= tmpdict0])
        right0 = total - left0

        if (left0 < minsize) or (right0 < minsize):
            print "ErrorMessage: mingroupsize is not satisfied!"
            raise SystemExit
        else :
            leftdata0  = freqtable[freqtable.Cut <= tmpdict0]
            leftdata0.index = np.arange(len(leftdata0))
            rightdata0 = freqtable[freqtable.Cut > tmpdict0]
            rightdata0.index = np.arange(len(rightdata0))
            cutlist.append(tmpdict0)

            if (left0 >= 2*minsize) & (len(leftdata0) > 2):
                tmpdict1 = self.calsplit(leftdata0)
                left1  = sum(leftdata0.Count[leftdata0.Cut <= tmpdict1])
                right1 = left0 - left1
                if (left1 >= minsize) & (right1 >= minsize):
                    cutlist.insert(0, tmpdict1)
                    
            if (right0 >= 2*minsize) & (len(rightdata0) > 2):
                tmpdict2 = self.calsplit(rightdata0)
                left2  = sum(rightdata0.Count[rightdata0.Cut <= tmpdict2])
                right2 = right0 - left2

                if (left2 >= minsize) & (right2 >= minsize):
                    cutlist.append(tmpdict2)
        cutlist.sort()
        print (cutlist)
        return [cutlist, freqtable]
    
    def calwoe(self, workbook):

        ############  Calculate WOE ###############
        woetable = pd.DataFrame()
        groupname = list()
        groupvalue = list()
        Count  = list()
        Eventcnt = list()
        Noeventcnt = list()
        woevalues = list()
        eventcnt = list()
        noeventcnt = list()
        total = list()
        tmpiv = 0.
        lastvalue = 0.
        sql = ""
        sqlfile = codecs.open(self.sqlpath, 'a')
        sqlfile.writelines("")


        format=workbook.add_format() 
        format.set_border(1) 
        format_title=workbook.add_format() 
        format_title.set_border(2) 
        format_title.set_bg_color('#cccccc') 
            
        format_title.set_align('center') 
        format_title.set_bold() 
        format_title.set_num_format('00000000') 
        
        format_ave=workbook.add_format() 
        format_ave.set_border(1) 
        format_ave.set_num_format('0.00') 
        
        if self.string_tag == 0:
            splitinfo = self.split()
            cutlist   = splitinfo[0]
            groupdata = splitinfo[1]
            totalevent = 1.*sum(groupdata.Count[groupdata[self.yname] == 1])
            totalnoevent = 1.*sum(groupdata.Count[groupdata[self.yname] == 0])
            
            for i, value in enumerate(cutlist):
                groupname.append(i+1)
                Count = sum(groupdata.Count[groupdata.Cut <= value])
                if i == 0 :
                    groupvalue.append(self.xname[:-4] +" <= " +str(value))
                    if self.cnt == 0:
                        sql = "  case when "+ self.xname[:-4] +" <= " +str(value)
                    else :
                        sql = " ,case when "+ self.xname[:-4] +" <= " +str(value)
                    _tmpevent   = sum(groupdata.Count[(groupdata.Cut <= value) & (groupdata[self.yname] == 1)])
                    _tmpnoevent = sum(groupdata.Count[(groupdata.Cut <= value) & (groupdata[self.yname] == 0)])
                else :
                    groupvalue.append("( "+ str(lastvalue)+ " < " + self.xname[:-4] + " <= " +str(value) + "]" )
                    sql = "       when "+self.xname[:-4]+" > "+str(lastvalue)+" and "+self.xname[:-4]+" <= "+str(value)
                    _tmpevent   = sum(groupdata.Count[(groupdata.Cut <= value) & (groupdata[self.yname] == 1) & (groupdata.Cut > cutlist[i-1])])
                    _tmpnoevent = sum(groupdata.Count[(groupdata.Cut <= value) & (groupdata[self.yname] == 0) & (groupdata.Cut > cutlist[i-1])])
                
                lastvalue = value
                
                _tmpwoevalue = np.log((_tmpevent/totalevent)/(_tmpnoevent/totalnoevent))
                tmpiv = tmpiv + (_tmpevent/totalevent - _tmpnoevent/totalnoevent)*_tmpwoevalue
                Eventcnt.append(_tmpevent)
                Noeventcnt.append(_tmpnoevent)
                woevalues.append(_tmpwoevalue)
                sql = sql+" then " + str(_tmpwoevalue)
                
                sqlfile.writelines(sql+"\n")
            
            #***** i = len(cutlist) ****
            groupname.append(i+2)
            Count = (totalevent + totalnoevent)
            groupvalue.append(self.xname[:-4] +" > " + str(value))
            sql = "       when "+self.xname[:-4] +" > " + str(value)
            _tmpevent   = sum(groupdata.Count[(groupdata.Cut > value) & (groupdata[self.yname] == 1)])
            _tmpnoevent = sum(groupdata.Count[(groupdata.Cut > value) & (groupdata[self.yname] == 0)])
            _tmpwoevalue = np.log((_tmpevent/totalevent)/(_tmpnoevent/totalnoevent))
            tmpiv = tmpiv + (_tmpevent/totalevent - _tmpnoevent/totalnoevent)*_tmpwoevalue
            Eventcnt.append(_tmpevent)
            Noeventcnt.append(_tmpnoevent)
            woevalues.append(_tmpwoevalue)
            sql = sql+" then "+str(_tmpwoevalue)
            sqlfile.writelines(sql+"\n")
            
                        
        else :
            strdata   = self.freq()
            groupdata = strdata['freqtable']
            cutlist = list(set(groupdata["Cut"]))
            totalevent = 1.*sum(groupdata.Count[groupdata[self.yname] == 1])
            totalnoevent = 1.*sum(groupdata.Count[groupdata[self.yname] == 0])
            
            for i, value in enumerate(cutlist):
                groupname.append(i+1)
                Count = sum(groupdata.Count[groupdata.Cut == value])
                groupvalue.append(self.xname[:-4] + " = " + str(value))
                if i == 0:
                    if self.cnt == 0:
                        sql = " case when "+ self.xname[:-4] + " = " + str(value)
                    else :
                        sql = " ,case when "+ self.xname[:-4] + " = " + str(value)
                else :
                    sql = "       when "+self.xname[:-4] + " = " + str(value)
                _tmpevent = sum(groupdata.Count[(groupdata.Cut == value) & (groupdata[self.yname] == 1)])
                _tmpnoevent = sum(groupdata.Count[(groupdata.Cut == value) & (groupdata[self.yname] == 0)])
                _tmpwoevalue = np.log((_tmpevent/totalevent)/(_tmpnoevent/totalnoevent))
                tmpiv = tmpiv + (_tmpevent/totalevent - _tmpnoevent/totalnoevent)*_tmpwoevalue
                
                Eventcnt.append(_tmpevent)
                Noeventcnt.append(_tmpnoevent)
                woevalues.append(_tmpwoevalue)
                sql = sql+" then "+str(_tmpwoevalue)
                sqlfile.writelines(sql+"\n")

        if len(self.nandata) > 0:
            groupname.append(i+3)
            groupvalue.append("missing")
            Count = len(self.nandata)
            _tmpevent = sum(self.nandata[self.yname])
            _tmpnoevent = Count - _tmpevent
            _tmpwoevalue = np.log((_tmpevent/totalevent)/(_tmpnoevent/totalnoevent))
            tmpiv = tmpiv + (_tmpevent/totalevent - _tmpnoevent/totalnoevent)*_tmpwoevalue
            Eventcnt.append(_tmpevent)
            Noeventcnt.append(_tmpnoevent)
            woevalues.append(_tmpwoevalue)
            sql = "       when "+self.xname[:-4]+" = missing then "+str(_tmpwoevalue)+" end as "+self.xname[:-4]+"_woe"
        else :
            sql = "       else 0.0000 end as "+self.xname[:-4]+"_woe"        
        sqlfile.writelines(sql+"\n")
        woetable["Groups"]  = groupname
        woetable["Cutoff"] = groupvalue
        woetable["Bad"]  = Eventcnt
        woetable["Good"]  = Noeventcnt
        woetable["WOE"]  = woevalues
        
        # **** Print WOE Chart ****
        if tmpiv >= 0.01 :
            plt.figure(self.cnt)
            plt.subplot(1,2,1)
            axi = np.arange(len(groupname))+1.1
            plt.xticks(axi, groupname)
            plt.plot(axi, woevalues, 'bo-')
            plt.grid(True)
            plt.title('WOE')
            plt.ylabel('WOE Value')
            plt.xlabel('Group')
            plt.subplot(1,2,2)
            plt.xticks(axi, groupname)
            bar1 = plt.bar(axi, Noeventcnt, width=0.5,align='center', color='b')
            bar2 = plt.bar(axi, Eventcnt, width=0.5,align='center', color='m')
            plt.legend((bar1[0], bar2[0]), ('noevent','event'))
            plt.grid(True)
            plt.title('Group Distribution')
            plt.ylabel('Count')
            plt.xlabel('Group')
            plt.savefig(self.xname[:-4]+'.png', dpi = 72)
            #plt.show() 
            # export woe_table and chart into xlsx file
            worksheet1  = workbook.add_worksheet(self.xname[:-4])
            worksheet1.write_row(0, 0, woetable, format_title)
            for i in np.arange(len(woetable)):
                worksheet1.write_row(i+1, 0, woetable.values[i], format)
            worksheet1.insert_image('G1', self.xname[:-4]+'.png')     
        return [woetable, tmpiv]
    

