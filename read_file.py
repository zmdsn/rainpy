# HAPPY CODING
#******* Y༺࿈༻Y ******************************************
#       /  ♅  \     Author        :  zmdsn
#  *    )0 ^ 0(     Last modified :  2022-01-26 09:33
#   \    \ - /      Email         :  zmdsn@126.com
#    \___ | | ___   Filename      :  read_file.py
#        \ ∵ /   L  Description   :
#        / ∴ \  }O{    
#       / | \ \  T       
# ******* |  \ ******************************************/
#!/usr/bin/python
# -*- coding: utf-8 -*- 
import pandas as pd
import chardet 
import time
import numpy as np 
import os
import sys
Debug = 1 

def run_time(func):
    def time_second(*args,**kwargs):
        start_time = time.time()
        res = func(*args,**kwargs)
        end_time = time.time()
        if Debug == 1:
            print( func.__name__, ' time used: ' ,end_time - start_time)
        return res
    return time_second

@run_time
def get_encoding(file):     
    # 验证基本没有用
    with open(file,'rb') as f:         
        tmp = chardet.detect(f.read(100))         
        print(tmp,tmp['encoding'])
        encoding = tmp['encoding']
        print(encoding)
        if tmp['confidence']<0.5 : 
            encoding = 'utf8'
        if encoding == 'ascii':
            encoding = 'utf8'
        if 'Windows' in encoding:
            encoding = 'gbk'
        return encoding

@run_time
def get_csv(file_name,skiprows=0, nrows=-1):
    # read_csv for different encoding, maybe rewite
    # encoding = get_encoding(fullPath)    
    if nrows < 0:
        try:
            data = pd.read_csv(file_name,skiprows=skiprows)
        except:             
            try:                 
                data = pd.read_csv(file_name,skiprows=skiprows,
                        encoding='gbk')
            except:                 
                data = pd.read_csv(file_name,skiprows=skiprows,
                        eencoding='gb2312')
    else :
        # print(nrows)
        try:
            data = pd.read_csv(file_name,skiprows=skiprows,nrows=nrows)
        except:             
            try:                 
                data = pd.read_csv(file_name,skiprows=skiprows,
                        nrows=nrows,encoding='gbk')
            except:                 
                data = pd.read_csv(file_name,skiprows=skiprows,
                        nrows=nrows,eencoding='gb2312')
    return data

@run_time
def get_excel(file_name,sheet_name=0):
    if sheet_name == 0:
        res = pd.read_excel(file_name)
    else:
        res = pd.read_excel(file_name,sheet_name)
    return res

def get_file_size(file_name):
    # size = sys.getsizeof(file_name)
    file_size = os.path.getsize(file_name)
    return file_size 

def print_file_size(file_name) :
    num = get_file_size(file_name)
    num_len = len(str(num))
    if (num_len<=3):
        print(str(num_len) )
    elif num_len>3 and (num_len<=6):
        print(str(round(num/1024,2)) + 'K')
    elif num_len>6 and (num_len<=9):
        print(str(round(num/1024**2,2)) + 'M')
    elif num_len>9 and (num_len<=12):
        print(str(round(num/1024**3,2)) + 'G')
    elif num_len>12 :
        print(str(round(num/1024**4,2)) + 'T')

def read_file(file_name,sheet=0,key=0,nrows=-1):
    # filename,type = os.path.splitext(path) 
    if 'csv' in file_name:
        data = get_csv(file_name,nrows=nrows)
    elif '.xlsx' in file_name or ('.xls' in file_name) :
        data = get_excel(file_name,sheet)
    elif '.pkl' in file_name:
        data = pd.read_pickle(file_name)
    elif 'h5' in file_name:
        if key == 0:
            data = pd.read_hdf(file_name)
        else:
            data = pd.read_hdf(file_name,key=key)
    return data

def name2csv(file_name,sheet=0):
    # filename,type = os.path.splitext(path) 
    if '.csv' in file_name:
        return file_name
    elif '.xlsx' in file_name:
        return file_name.replace('.xlsx','_') + str(sheet)+ '.csv' 
    elif '.xls' in file_name:
        return file_name.replace('.xls','_') + str(sheet) + '.csv' 
    elif '.pkl' in file_name:
        return file_name.replace('.pkl','.csv')
    elif '.h5' in file_name:
        return file_name.replace('.h5','.csv')

def read_data(file_name,sheet=0,key=0,nrows=-1):
    csv_name = name2csv(file_name,sheet)
    if os.path.exists(csv_name):
        data = read_file(csv_name,nrows=nrows)
        return data
    else:
        data = read_file(file_name,sheet,key,nrows)
        data.to_csv(csv_name,index=None)
        return data
    return 'No this file'

if __name__ == '__main__':
    fpath = "../" 
    # fname = "标记是否异常值剔除.csv"     
    # fname = "poi未匹配.csv"     
    # fname = "重复村名.xlsx"     
    fname = "重复村名.xlsx"     
    fullPath = fpath + fname     
    # print(get_encoding(fullPath) )    
    # print(get_encoding('test.csv') )    
    # df = get_csv(fullPath)
    # size = os.path.getsize('test.csv')
    # print(size)
    # df = get_csv('test.csv')
    # print(df.memory_usage().sum())
    # df . to_pickle('test.pkl')
    # df = pd.read_pickle('test.pkl')
    # print(df.memory_usage().sum())
    # print(get_file_size(fullPath))
    print_file_size(fullPath)
    # read_data('test.csv',nrows=2200)
    # read_data(fullPath)
    # df = get_csv('test.gz')
    # combine = np.random.rand(2000000,100)
    # print(sys.getsizeof(combine))
    # a = pd.DataFrame(combine)
    # # a.to_csv('test.csv')
    # a.to_csv('test.gz', compression='gzip', index=False)
