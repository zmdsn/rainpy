import numpy as np
from rainpy.ts import *
from rainpy import read
import pandas as pd
import pytest


@pytest.fixture
def sample_data():
    # 示例数据 - 不同精度的时间戳
    timestamps = {
        'seconds': [1609459200, 1609545600, 1609632000],      # 秒级
        'milliseconds': [1609459200000, 1609545600000, 1609632000000],  # 毫秒级
        # 微秒级
        'microseconds': [1609459200000011, 1609545600000000, 1609632000000000]
    }
    df = pd.DataFrame(timestamps)
    return df


@pytest.fixture
def sample_df():
    file_path = "tests/test_data/ETTh1.csv"
    df = read_data(file_path)
    return df


@pytest.fixture
def df_discontinuous():
    # 生成连续的时间序列
    date_rng = pd.date_range(start='2024-01-01', end='2024-01-10', freq='H')
    data = np.random.randn(len(date_rng))

    # 创建DataFrame
    df_continuous = pd.DataFrame(data, columns=['value'], index=date_rng)
    np.random.seed(42)  # 保证可重复性
    mask = np.random.random(len(df_continuous)) > 0.3
    df_discontinuous = df_continuous[mask]
    return df_discontinuous


def test_get_datetime_column(sample_data):
    a, b, c = get_datetime_column(sample_data)
    assert a == 'seconds'  # 假设秒级时间戳被选为索引
    assert c == 's'  # 假设秒级时间戳被选为索引


def test_set_datetime_index(sample_data):
    df = set_datetime_index(sample_data)
    assert df.index. name == 'seconds'  # 假设秒级时间戳被选为索引
    assert df.index[0] == pd.to_datetime(1609459200, unit='s')


def test_set_datetime_index1(sample_data):
    df = set_datetime_index(sample_data, datetime_col='milliseconds')
    assert df.index.name == 'milliseconds'  # 假设秒级时间戳被选为索引
    assert df.index[0] == pd.to_datetime(1609459200000, unit='ms')


def test_set_datetime_index2(sample_data):
    df = set_datetime_index(sample_data, datetime_col='microseconds')
    assert df.index.name == 'microseconds'  # 假设秒级时间戳被选为索引
    assert df.index[0] == pd.to_datetime(1609459200000011, unit='us')


def test_read_data(file_path="tests/test_data/ETTh1.csv"):
    df = read_data(file_path)
    assert df.index.name == 'date'  # 假设秒级时间戳被选为索引


def test_read_data_error(file_path="tests/test_data/csv_utf8_t.csv"):
    with pytest.raises(ValueError):
        df = read_data(file_path)


def test_is_uniform_sampling(sample_df, df_discontinuous):
    assert is_uniform_sampling(sample_df) == True  # 假设数据是均匀采样的，时间差唯一
    print(df_discontinuous)
    assert is_uniform_sampling(df_discontinuous) == False  # 非均匀采样


def test_has_missing_data(sample_df, df_discontinuous):
    assert has_missing_data(sample_df) == False  # 假设数据没有缺失
    assert has_missing_data(df_discontinuous) == False  # 人为制造缺失


def test_has_duplicate_timestamps(sample_df, df_discontinuous):
    assert has_duplicate_timestamps(sample_df) == False  # 假设数据没有重复时间戳
    # 制造重复时间戳
    df_dup = df_discontinuous._append(df_discontinuous.iloc[0])
    assert has_duplicate_timestamps(df_dup) == True  # 存在重复时间戳


def test_is_time_index_continuous(sample_df, df_discontinuous):
    assert is_time_index_continuous(sample_df) == True
    assert is_time_index_continuous(df_discontinuous) == False


def test_resample_time_series(df_discontinuous):
    df_resampled = resample_time_series(df_discontinuous, 'H')
    assert is_time_index_continuous(df_resampled) == True
    assert df_resampled.shape[0] >= df_discontinuous.shape[0]  # 重采样后行数应不少于原始数据


def test_z_score_detection(sample_df):
    series = sample_df['OT']
    anomalies = z_score_detection(series, threshold=3)
    assert isinstance(anomalies, pd.Series)  # 返回值应为Series类型
    assert not anomalies.empty  # 应至少检测到一些异常点


def test_iqr_detection(sample_df):
    series = sample_df['OT']
    anomalies = iqr_detection(series)
    assert isinstance(anomalies, pd.Series)  # 返回值应为Series类型
    assert not anomalies.empty


def test_check_gaussian_assumption(sample_df):
    series = sample_df['OT']
    result, image_base64 = check_gaussian_assumption(series)
    assert result[series.name] == True

    df_sel = sample_df[['OT', 'HULL']]
    result, image_base64 = check_gaussian_assumption(df_sel)
    assert result['OT'] == True
    assert result['HULL'] == True


def test_analyze_missing_data(df_discontinuous):
    analysis = analyze_missing_data(df_discontinuous)
    assert 'total_missing' in analysis
    assert 'missing_ratio' in analysis
    assert 'missing_pattern' in analysis
    assert 'consecutive_missing' in analysis


