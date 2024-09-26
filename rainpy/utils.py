
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




