from io import StringIO
import re
from email import charset
import inspect
import json
import os
import pandas as pd
import pytest
from types import FunctionType
import jsonlines
import chardet
from .utils import get_defined_functions


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
    use_pandas = kwargs.get("pandas", True)
    if not use_pandas:
        filter_kwargs = get_func_paramate(jsonlines.open, **kwargs)
        if kwargs.get('lines'):
            return read_jsonl_generator(file, *args, **filter_kwargs)
        with jsonlines.open(file, *args, **filter_kwargs) as reader:
            read_list = [x for x in reader]
            return read_list
    else:
        return pd.read_json(file, lines=True)


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


pandas_first_ext = [".csv", ".xlsx", ".xls", ".hdf", ".orc",
                    ".parquet", ".sql", ".feather",  # ".html",
                    ".xml", ".sas", ".spss",
                    ".pkl", ".fwf", ".stata"]


def _detect_delimiter(file_path, encoding=None, sample_lines=5):
    """
    自动检测文件的分隔符
    返回：',' '\t' ' ' 或 'unknown'
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = [f.readline().strip()
                     for _ in range(sample_lines) if f.readline()]
        if not lines:
            return ' '  # 默认返回空格
        # 统计各种分隔符的出现频率
        delimiter_counts = {
            ',': 0,
            '\t': 0,
            ' ': 0,
            ';': 0
        }
        for line in lines:
            if line:  # 跳过空行
                for delim in delimiter_counts:
                    delimiter_counts[delim] += line.count(delim)
        # 返回出现最多的分隔符
        most_common = max(delimiter_counts.items(), key=lambda x: x[1])
        # 如果最常见的分隔符出现次数为0，可能是固定宽度文件
        if most_common[1] == 0:
            return None  # 默认使用空格分隔
        return most_common[0]
    except Exception:
        return None  # 发生错误时返回默认值


def pd_read(file, *args, **kwargs):
    if "encoding" not in kwargs:
        encoding = get_encoding(file)
        kwargs['encoding'] = encoding
    ext = get_extension(file)
    pd_ext = read_map.get(ext, ext.replace(r".", ""))
    func = f"read_{pd_ext}"
    if hasattr(pd, func):
        try:
            if pd_ext == "csv" and "sep" not in kwargs:
                kwargs["sep"] = _detect_delimiter(file, kwargs.get('encoding'))
                kwargs["engine"] = "c"
                if not kwargs["sep"]:
                    kwargs["engine"] = "python"
            elif pd_ext in ['tsv', 'tab']:
                kwargs["sep"] = "\t"
                kwargs["engine"] = "c"
            function = getattr(pd, func)
            filter_kwargs = get_func_paramate(function, **kwargs)
            return function(file, *args, **filter_kwargs)
        except Exception as e:
            raise RuntimeError from e


def read(file, *args, **kwargs):
    try:
        return read_file(file, *args, **kwargs)
    except FileNotFoundError:
        return read_string(file, *args, **kwargs)


def read_string(md_string, *args, **kwargs):
    is_markdown_table = analyze_markdown_table_structure(md_string)
    if is_markdown_table:
        return read_markdown(md_string, *args, **kwargs)
    else:
        from io import StringIO
        return pd.read_csv(StringIO(md_string), *args, **kwargs)


def read_file(file, *args, **kwargs):
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


def test_get_func_paramate():
    assert get_func_paramate("get_xx") == {}
    assert get_func_paramate("get_xx", a=3) == {}
    assert get_func_paramate("get_xx", a=3, b=4) == {}
    # assert get_func_paramate(get_xx) == {}
    # assert get_func_paramate(get_xx, a=3) == {}
    # assert get_func_paramate(get_xx, a=3, b=4) == {}
    # assert get_func_paramate(get_xx, xx=3, b=4) == {"xx": 3}
    # assert get_func_paramate(get_xx, xx=3) == {"xx": 3}
    # assert get_func_paramate(get_xx, xx=3, cx=4) == {"xx": 3, "cx": 4}


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


def is_table_data_row(line):
    """判断是否为表格数据行"""
    if '|' in line:
        # 管道格式的表格行
        cells = [cell.strip()
                 for cell in line.strip('|').split('|') if cell.strip()]
        return len(cells) >= 2
    else:
        # 无管道格式的表格行（至少包含两个单词）
        words = line.split()
        return len(words) >= 2


def is_table_separator(line):
    """判断是否为表格分隔行"""
    line_clean = line.replace(' ', '')
    # 匹配 |---|, |:---|, |:---:|, |---:| 等格式
    separator_pattern = r'^\|?(\s*:?-+:?\s*\|?)+$'
    return re.match(separator_pattern, line_clean) is not None


def analyze_markdown_table_structure(text):
    """
    详细分析字符串的 Markdown 表格结构特征
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if len(lines) < 2:
        return {"is_table": False, "reason": "行数不足"}
    features = {
        "has_pipes": False,
        "has_separator": False,
        "consistent_columns": False,
        "has_header": False,
        "has_data": False
    }
    # 检查是否使用管道符
    pipe_lines = [line for line in lines if '|' in line]
    features["has_pipes"] = len(pipe_lines) > 0
    # 检查分隔行
    for i, line in enumerate(lines):
        if is_table_separator(line):
            features["has_separator"] = True
            # 分隔行应该在表头之后
            if i == 1 and len(lines) > 2:
                features["has_header"] = True
    # 检查列数一致性
    if features["has_pipes"]:
        column_counts = []
        for line in pipe_lines:
            if not is_table_separator(line):
                cells = [cell for cell in line.strip(
                    '|').split('|') if cell.strip()]
                column_counts.append(len(cells))
        if column_counts:
            features["consistent_columns"] = len(set(column_counts)) == 1
    # 检查是否有数据行
    data_lines = [line for line in lines if is_table_data_row(
        line) and not is_table_separator(line)]
    features["has_data"] = len(data_lines) >= 1
    # 综合判断
    score = sum(features.values())
    is_table = score >= 3  # 至少满足3个特征
    return is_table


def read_markdown(md_string, dtype_conversion=True):
    """
    将 Markdown 表格字符串转换为 pandas DataFrame
    参数:
    md_string: Markdown 表格字符串
    dtype_conversion: 是否尝试自动转换数据类型
    返回:
    pandas DataFrame
    """
    # 清理输入字符串
    md_string = md_string.strip()
    # 分割行
    lines = md_string.split('\n')
    # 识别表头和分隔行
    header_line = None
    data_lines = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # 检查是否为分隔行（包含 --- 或 :-- 等）
        if re.match(r'^\|?(\s*:?-+:?\s*\|?)+$', line.replace(' ', '')):
            continue
        # 第一行非空行作为表头
        if header_line is None:
            header_line = line
        else:
            data_lines.append(line)
    if header_line is None:
        raise ValueError("未找到有效的表头")
    # 处理表头
    headers = [h.strip() for h in header_line.strip('|').split('|')]
    # 处理数据行
    data = []
    for line in data_lines:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) == len(headers):
            data.append(cells)
    # 创建 DataFrame
    df = pd.DataFrame(data, columns=headers)
    # 尝试自动转换数据类型
    if dtype_conversion:
        for col in df.columns:
            # 尝试转换为数值
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                # 尝试转换为日期
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    # 保持为字符串
                    pass
    return df


__all__ = get_defined_functions()
