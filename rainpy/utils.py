
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
