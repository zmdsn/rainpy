from email import charset
import json
import os
import pandas as pd
import pytest
from types import FunctionType
import jsonlines
import  chardet


def get_xx(xx, cx):
    print(xx, cx)
    pass


def func_paramate(
        func_name: str | FunctionType,
        **kwarg):
    parameter_set = set()
    if isinstance(func_name, FunctionType):
        parameter_set = set(func_name.__code__.co_varnames)
    elif isinstance(func_name, str):
        parameter_set = set(eval(f"{func_name}.__code__.co_varnames"))
    if isinstance(kwarg, dict):
        keys = parameter_set & set(kwarg.keys())
        return {k: kwarg.get(k) for k in keys}
    return {}


def get_extension(file_path):
    return os.path.splitext(file_path)[-1]


def read_text(file, *args, **kwargs):
    filter_kwargs = func_paramate(open, **kwargs)
    with open(file, *args, **filter_kwargs) as f:
        if kwargs.get('lines'):
            return f.readlines()
        return f.read()


def read_jsonl_generator(file, *args, **kwargs):
    with jsonlines.open(file, *args, **kwargs) as reader:
        for x in reader:
            yield x


def read_jsonl(file, *args, **kwargs):
    filter_kwargs = func_paramate(jsonlines.open, **kwargs)
    del filter_kwargs['encoding']
    if kwargs.get('lines'):
        with jsonlines.open(file, *args, **filter_kwargs) as reader:
            read_list = [x for x in reader]
            return read_list
    return read_jsonl_generator(file, *args, **filter_kwargs)


def read_json(file, *args, **kwargs):
    filter_kwargs = func_paramate(jsonlines.open, **kwargs)
    with open(file, *args, **filter_kwargs) as f:
        try:
            content = json.load(f)
        except Exception as e:
            raise e from e
    return content


def get_encoding(file):
    with open(file, 'rb') as f:
        enc_dict = chardet.detect(f.read(2000))
        if enc_dict.get("confidence") < 0.8 and enc_dict.get("encoding") == 'ISO-8859-1':
            return "GBK"
        return enc_dict.get("encoding", 'utf8')
    

def pd_read_excel(filename, **kwargs):
    encodings = ['utf-8', 'gbk',  'utf-8-sig', 'GB2312', 'gb18030',]
    filter_kwargs = func_paramate(pd.read_excel, **kwargs)

    data = pd.DataFrame()
    for encoding in encodings:
        try:
            if kwargs.get("encoding"):
                data = pd.read_excel(filename, **filter_kwargs)
                return data
            kwargs['encoding'] = encoding
            data = pd.read_excel(filename, **filter_kwargs)
            return data
        except Exception as e:
            print(filename, e)
    return data


def read(file, *args, **kwargs):
    ext = get_extension(file)
    if "encoding" not in kwargs:
        encoding = get_encoding(file)
        kwargs['encoding'] = encoding
        
    if ext == ".jsonl":
        data = read_jsonl(file, *args, **kwargs)
        if kwargs.get('pandas'):
            return pd.DataFrame(data)
        return data
    
    if ext == ".json":
        return read_json(file, *args, **kwargs)

    if ext in [".xlsx", ".xls"]:
        return pd_read_excel(file, *args, **kwargs)

    data = read_text(file, *args, **kwargs)
    if ext == ".csv":
        return pd.DataFrame(data)

    return data

def test_func_paramate():
    assert func_paramate("get_xx") == {}
    assert func_paramate("get_xx", a=3) == {}
    assert func_paramate("get_xx", a=3, b=4) == {}
    assert func_paramate(get_xx) == {}
    assert func_paramate(get_xx, a=3) == {}
    assert func_paramate(get_xx, a=3, b=4) == {}
    assert func_paramate(get_xx, xx=3, b=4) == {"xx": 3}
    assert func_paramate(get_xx, xx=3) == {"xx": 3}
    assert func_paramate(get_xx, xx=3, cx=4) == {"xx": 3, "cx": 4}


def test_read_text():
    pass


def test_read():
    pass
    # read("or_example_gbk.json")
