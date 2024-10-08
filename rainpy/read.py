from email import charset
import inspect
import json
import os
import pandas as pd
import pytest
from types import FunctionType
import jsonlines
import chardet


def get_xx(xx, cx):
    print(xx, cx)
    pass


def get_parameters(func):
    parameters = {}
    if isinstance(func, FunctionType):
        parameters = inspect.signature(func).parameters
    elif isinstance(func, str):
        parameters = inspect.signature(eval(func)).parameters
    return set(parameters.keys())


def get_func_paramate(
        func_name: str | FunctionType,
        **kwarg):
    parameter_set = get_parameters(func_name)
    if isinstance(kwarg, dict):
        keys = parameter_set & set(kwarg.keys())
        return {k: kwarg.get(k) for k in keys}
    return {}


def get_extension(file_path):
    return os.path.splitext(file_path)[-1]


def read_text(file, *args, **kwargs):
    filter_kwargs = get_func_paramate(open, **kwargs)
    with open(file, *args, **filter_kwargs) as f:
        if kwargs.get('lines'):
            return f.readlines()
        return f.read()


def read_jsonl_generator(file, *args, **kwargs):
    with jsonlines.open(file, *args, **kwargs) as reader:
        for x in reader:
            yield x


def read_jsonl(file, *args, **kwargs):
    filter_kwargs = get_func_paramate(jsonlines.open, **kwargs)
    if kwargs.get('lines'):
        with jsonlines.open(file, *args, **filter_kwargs) as reader:
            read_list = [x for x in reader]
            return read_list
    return read_jsonl_generator(file, *args, **filter_kwargs)


def read_json(file, *args, **kwargs):
    filter_kwargs = get_func_paramate(jsonlines.open, **kwargs)
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
    filter_kwargs = get_func_paramate(pd.read_excel, **kwargs)

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


read_map = {
    ".txt": "table",
    ".pkl": "pickle",
    '.xlsx': "excel",
    '.xls': "excel",
}

write_map = {
    ".pkl": "pickle",
    '.xlsx': "excel",
    '.xls': "excel",
}

pandas_first_ext = [".csv", ".xlsx", ".xls", ".hdf", ".orc",
                    ".parquet", ".sql", ".feather",  # ".html",
                    ".xml", ".sas", ".spss",
                    ".pkl", ".fwf", ".stata"]


def pd_read(file, *args, **kwargs):
    if "encoding" not in kwargs:
        encoding = get_encoding(file)
        kwargs['encoding'] = encoding
    ext = get_extension(file)
    pd_ext = read_map.get(ext, ext.replace(r".", ""))
    func = f"read_{pd_ext}"
    if hasattr(pd, func):
        try:
            function = getattr(pd, func)
            filter_kwargs = get_func_paramate(function, **kwargs)
            return function(file, *args, **filter_kwargs)
        except Exception as e:
            raise RuntimeError from e


def read(file, *args, **kwargs):
    ext = get_extension(file)
    if "encoding" not in kwargs:
        encoding = get_encoding(file)
        kwargs['encoding'] = encoding

    # Pay attention to the order
    if ext == ".jsonl":
        data = read_jsonl(file, *args, **kwargs)
        if kwargs.get('pandas'):
            return pd.DataFrame(data)
        return data

    if kwargs.get('pandas'):
        return pd_read(file, *args, **kwargs)

    if ext in pandas_first_ext:
        try:
            return pd_read(file, *args, **kwargs)
        except:
            return read_text(file, *args, **kwargs)

    if ext == ".json":
        return read_json(file, *args, **kwargs)

    data = read_text(file, *args, **kwargs)
    return data


def pd_save(file, data, *args, **kwargs):
    ext = get_extension(file)
    if "index" not in kwargs:
        kwargs['index'] = False
    pd_ext = write_map.get(ext, ext.replace(r".", ""))
    func = f"to_{pd_ext}"

    if hasattr(data, func):
        try:
            if isinstance(data, pd.DataFrame):
                function = getattr(pd.DataFrame, func)
            elif isinstance(data, pd.Series):
                function = getattr(pd.Series, func)
            filter_kwargs = get_func_paramate(function, **kwargs)
            function = getattr(data, func)
            function(file, *args, **filter_kwargs)
        except Exception as e:
            raise RuntimeError from e
    else:
        raise RuntimeError(f"Pandas does not support the suffix : '{ext}'\n")


def check_dirs(file):
    dirs = os.path.dirname(file)
    if not os.path.exists(dirs):
        os.makedirs(dirs)


def write(file, data, *args, **kwargs):
    save(file, data, *args, **kwargs)


def save_txt(file, data, mode='w'):
    with open(file, mode) as f:
        f.write(data)


def save_json(file, data, mode='w', *args, **kwargs):
    with open(file, mode) as f:
        json.dump(data, f, *args, **kwargs)


def save_jsonl(file, data, mode='w', *args, **kwargs):
    mode = kwargs.get("mode", 'w')
    if "mode" not in kwargs:
        mode = 'w'
        if os.path.exists(file) and os.path.getsize(file):
            mode = 'a'
    with jsonlines.open(file, mode=mode) as writer:
        writer.write(data)


def save(file, data, *args, **kwargs):
    if not file:
        raise RuntimeError(f"No file specified\n")
    check_dirs(file)
    ext = get_extension(file)
    if "encoding" not in kwargs:
        kwargs['encoding'] = 'utf8'

    if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
        return pd_save(file, data, *args, **kwargs)

    if ext == ".jsonl":
        save_jsonl(file, data, *args, **kwargs)
        return

    if ext == ".json":
        save_json(file, data, *args, **kwargs)
        return

    save_txt(file, data, *args, **kwargs)
    return


def test_get_func_paramate():
    assert get_func_paramate("get_xx") == {}
    assert get_func_paramate("get_xx", a=3) == {}
    assert get_func_paramate("get_xx", a=3, b=4) == {}
    assert get_func_paramate(get_xx) == {}
    assert get_func_paramate(get_xx, a=3) == {}
    assert get_func_paramate(get_xx, a=3, b=4) == {}
    assert get_func_paramate(get_xx, xx=3, b=4) == {"xx": 3}
    assert get_func_paramate(get_xx, xx=3) == {"xx": 3}
    assert get_func_paramate(get_xx, xx=3, cx=4) == {"xx": 3, "cx": 4}


def test_read_text():
    pass


def test_read():
    pass
    # read("or_example_gbk.json")


def get_files(path, type="*"):
    if r"*" in path or "?" in path:
        return [file for file in glob.glob(path)]
    if os.path.isdir(path):
        return [file for file in glob.glob(os.path.join(path, "*"+type))]
    elif os.path.isfile(path):
        return [path]

