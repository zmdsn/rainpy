from rainpy.ts import get_datetime_column, read_data, set_datetime_index
from rainpy import read
import pandas as pd
import pytest

@pytest.fixture
def sample_data():
    # 示例数据 - 不同精度的时间戳
    timestamps = {
        'seconds': [1609459200, 1609545600, 1609632000],      # 秒级
        'milliseconds': [1609459200000, 1609545600000, 1609632000000],  # 毫秒级
        'microseconds': [1609459200000011, 1609545600000000, 1609632000000000]  # 微秒级
    }
    df = pd.DataFrame(timestamps)
    return df

@pytest.fixture
def sample_df():
    file_path="tests/test_data/ETTh1.csv"
    df = read_data(file_path)
    return df


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

def test_set_datetime_index2(sample_data):
    df = set_datetime_index(sample_data, datetime_col='microseconds')
    assert df.index.name == 'microseconds'  # 假设秒级时间戳被选为索引
    assert df.index[0] == pd.to_datetime(1609459200000011, unit='us')

def test_read_data_(sample_df):
    print(sample_df.head(5))
    
