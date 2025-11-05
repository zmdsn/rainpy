import json
import os
import jsonlines
import pandas as pd

from .read import get_extension, get_func_paramate

write_map = {
    ".pkl": "pickle",
    '.xlsx': "excel",
    '.xls': "excel",
}

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
