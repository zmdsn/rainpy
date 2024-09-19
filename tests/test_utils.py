import pytest
from rainpy.raindrop import make_frame

from rainpy.utils import pd_read_csv


def test_pd_read_csv():
    df_gbk_t = pd_read_csv("tests/test_data/csv_gbk_t.csv",  sep="\t")
    df_gbk = pd_read_csv("tests/test_data/csv_gbk.csv")
    df_utf8 = pd_read_csv("tests/test_data/csv_utf8.csv")
    df_utf8_t = pd_read_csv("tests/test_data/csv_utf8_t.csv", sep="\t")
    
    all(df_utf8.fillna(0) == df_gbk.fillna(0))
    all(df_utf8_t.fillna(0) == df_utf8.fillna(0))
    all(df_utf8_t.fillna(0) == df_gbk_t.fillna(0))

    # df = pd_read_csv("judge_result0913.csv", chunksize=5)
    # for d in df:
    #     print(d.shape)

    # df = pd_read_csv("judge_result0913.csv", iterator=True)
    # df.get_chunk(7)
