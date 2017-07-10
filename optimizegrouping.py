import pandas as pd
import xlsxwriter
import prebin as pb
import grouping as gp
import codecs
import os


class optmizeGrouping(object):
    
    def optimzegrouping(self, datafile, xnames, target):
        
        data = pd.read_csv(datafile)
        dataname = datafile.split("/")[-1].split(".")[0]
        datapath = datafile.split(dataname)[:-1][0]
        os.system("rm -rf " + datapath + dataname)
        os.system("mkdir " + datapath +dataname)
        sqlpath = datapath + dataname+"/grouping_info.sql"
        os.system("touch " + sqlpath)
        woepath = datapath+dataname+"/woe_info.xlsx"
        
        workbook = xlsxwriter.Workbook(woepath)
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
        
        #IV_table = pd.DataFrame()
        IV_list = list()
        for i, xname in enumerate(xnames):
            ds = data[[target, xname]]
            g  = pb.prebin(data, xname, target, method = 'quantile')
            aa = g.binning()
            x_bin = xname+"_bin"
            print("Xname = " + xname)
            print(aa)
            bbb = gp.grouping(aa, target, x_bin, i, sqlpath, mingroupsize = 0.02)
            cvb = bbb.calwoe(workbook)
            #print("xname = " + xname)
            #print(cvb)
            #aa[0]
            #os.system("rm -rf "+x_bin[:-4]+'.png')
            IV_list.append(cvb[1])
        worksheet1  = workbook.add_worksheet("IV")
        worksheet1.write_row(0, 0, ["Vars", "IV"], format_title)
        worksheet1.write_column(1, 0, xnames, format)
        worksheet1.write_column(1, 1, IV_list, format)
        workbook.close()
       
