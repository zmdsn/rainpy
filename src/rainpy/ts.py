import pandas as pd

from rainpy import read


def quick_timestamp_check(value):
    """
    快速判断单个值是否为时间戳
    """
    value = float(value)

    # 常见时间戳范围判断
    if 1e9 <= value <= 2e9:
        return "s"
    elif 1e12 <= value <= 2e13:
        return "ms"
    elif 1e15 <= value <= 2e16:
        return "us"
    elif 10000000 <= value <= 29991231:
        return "YYYYMMDD"
    elif 3560 <= value <= 50000:
        return "可能是Excel日期"
    else:
        return False


def quick_timestamp_check_series(df):
    checks = df.apply(lambda x: quick_timestamp_check(x))
    return checks.mode()[0]


def _score_time_column(df, col, sample_size=20):
    """
    对单列计算时间列评分，返回 (score, reasons)
    """
    score = 0
    reasons = []

    # 1. 列名提示
    time_keywords = ['time', 'date', 'timestamp',
                     'datetime', 'created', 'updated']
    if any(keyword in col.lower() for keyword in time_keywords):
        score += 10
        reasons = "keyword"

    # 2. 已是 datetime 类型 或 可转换为 datetime
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        score += 50
        reasons = "datetime"
    elif df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
        sample = df[col].head(sample_size).dropna()
        if not sample.empty:
            try:
                converted = pd.to_datetime(sample, errors='coerce')
                # 若至少一半样本可转换，则认为可转换为时间
                if converted.notna().sum() >= max(1, int(len(sample) * 0.5)):
                    score += 50
                    reasons = "to_datetime"
            except:
                pass

    # 3. 高唯一性提示
    if len(df) > 0 and df[col].nunique() / len(df) > 0.8:
        score += 10

    # 4. 值范围检查（数值型）
    if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
        sample_vals = df[col].dropna().head(sample_size)
        if not sample_vals.empty:
            checks = sample_vals.apply(lambda x: quick_timestamp_check(x))
            # 返回出现频率最高的值
            if checks.all():
                score += 30
                reasons = checks.mode()[0]
    return score, reasons


def get_datetime_column(df, sample_size=50):
    """
    综合性的时间列检测，返回置信度最高的列名或 None
    """
    results = []
    for col in df.columns:
        score, reasons = _score_time_column(df, col, sample_size)
        if score > 0:
            results.append((col, score, reasons))
    if results:
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        if sorted_results[0][1] > 10:
            return sorted_results[0]
        raise ValueError("未检测到时间字段")
    else:
        # 未检测到时间列，按照函数文档返回 None
        raise ValueError("未检测到时间字段")


def set_datetime_index(df, datetime_col=None):
    if datetime_col:
        ds_type = quick_timestamp_check_series(df[datetime_col].head(20))
        if ds_type in ['s', 'ms', 'us']:
            df[datetime_col] = pd.to_datetime(df[datetime_col], unit=ds_type)
        else:
            df[datetime_col] = pd.to_datetime(df[datetime_col])
        df.set_index(datetime_col, inplace=True)
    else:
        datetime_col, _,  ds_type = get_datetime_column(df)
        if datetime_col:
            if ds_type in ['s', 'ms', 'us']:
                df[datetime_col] = pd.to_datetime(
                    df[datetime_col], unit=ds_type)
            else:
                df[datetime_col] = pd.to_datetime(df[datetime_col])
            df.set_index(datetime_col, inplace=True)
    return df


def read_data(file_path):
    df = read(file_path)
    df = set_datetime_index(df)
    return df


def describe(df):
    """
    产生描述性统计数据
    """
    if isinstance(df, str):
        df = read_data(df)
    return df.describe().to_json()


def is_uniform_sampling(df):
    """
    检查数据是否为均匀采样
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.shape[0] > 2:
        time_diff = df.index.to_series().diff()
        return len(time_diff[1:].unique())
    return False

# 是否缺失数据


def has_missing_data(df):
    """
    检查数据是否存在缺失
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.isnull().values.any():
        return True
    return False

# 是否存在重复时间戳


def has_duplicate_timestamps(df):
    """
    检查数据是否存在重复时间戳
    """
    if isinstance(df, str):
        df = read_data(df)
    if df.index.duplicated().any():
        return True
    return False

# 是否时间索引连续


def is_time_index_continuous(df):
    """
    检查时间索引是否连续
    """
    if isinstance(df, str):
        df = read_data(df)
    time_diff = df.index.to_series().diff().dropna()
    expected_diff = time_diff.mode()[0]
    discontinuities = time_diff[time_diff != expected_diff]
    if not discontinuities.empty:
        return False
    return True
