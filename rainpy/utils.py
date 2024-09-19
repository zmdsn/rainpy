
import pandas as pd


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
