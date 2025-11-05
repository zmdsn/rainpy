
import pandas as pd

def read_csv(filename: str, return_type: str = 'dict', iterator=False):
    # type : 'list', 'dict'
    encodings = ['utf-8', 'gbk',  'utf-8-sig', 'GB2312', 'gb18030',]
    data = []
    for encoding in encodings:
        try:
            with open(filename, encoding=encoding) as f:
                if return_type == 'dict':
                    reader = csv.DictReader(f)
                else:
                    reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if iterator:
                        yield row
                    data.append(row)
            return data
        except Exception as e:
            print(filename, e)
    return data

def pd_read_csv(filename, **kwargs):
    encodings = ['utf-8', 'gbk',  'utf-8-sig', 'GB2312', 'gb18030',]
    data = pd.DataFrame()
    for encoding in encodings:
        try:
            if kwargs.get("encoding"):
                data = pd.read_csv(filename, **kwargs)
                return data
            data = pd.read_csv(filename, encoding=kwargs.get("encoding", encoding), **kwargs)
            return data
        except Exception as e:
            print(filename, e)
    return data

def get_extension(file_path):
    return os.path.splitext(file_path)[-1]


def formatTime(atime):
    import time
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(atime))

fileinfo = os.stat(file_path)
print("最后一次访问时间:",formatTime(fileinfo.st_atime))
print("最后一次修改时间:",formatTime(fileinfo.st_mtime))
print("最后一次状态变化的时间：",formatTime(fileinfo.st_ctime))
print("索引号：",fileinfo.st_ino)
print("被连接数目：",fileinfo.st_dev)
print("文件大小:",fileinfo.st_size,"字节")
print("最后一次访问时间:",fileinfo.st_atime)
print("最后一次修改时间:",fileinfo.st_mtime)
print("最后一次状态变化的时间：",fileinfo.st_ctime)


import psutil
psutil.cpu_count() 
psutil.cpu_count(logical=False) 

psutil.virtual_memory()
psutil.disk_partitions()
psutil.disk_usage('/dev/sda1')

import sys

sys.getsizeof(dfe)



def calculate_tax(income, deduction=60000, additional_deduction=0):
    tax_rates = [(0, 0.03, 0), (36000, 0.1, 2520), (144000, 0.2, 16920), (300000, 0.25, 31920), (420000, 0.3, 52920), (660000, 0.35, 85920), (960000 , 0.45, 181920)]
    tax_rates.reverse()
    taxable_income = max(income - deduction - additional_deduction, 0)
    tax = 0
    for threshold, rate, des in tax_rates:
        if taxable_income >= threshold:
            tax = taxable_income * rate - des
            break
    return tax


def set_launch_env():
    path = ".vscode/launch.json"
    import json
    import os
    with open(path, 'r') as json_file:
        json_data = json.load(json_file)
    json_data

    env_variables = json_data.get('configurations', [{}])[0].get('env', {})
    for var_name, var_value in env_variables.items():
        os.environ[var_name] = os.environ.get(var_name, var_value)
    return env_variables