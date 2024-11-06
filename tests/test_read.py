import pytest
from rainpy import read

def test_read_csv():
    data = read("tests/test_data/test_one.json")
    assert data.get("age") == 25

    data = read("tests/test_data/test.jsonl")
    assert data.shape[0] == 3
    assert data['age'][0] == 25

    data = read("tests/test_data/test.json")
    assert data.shape[0] == 3
    assert data['age'][0] == 25














