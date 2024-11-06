import pytest
from rainpy import read

def test_read_jsonl():
    data = read("tests/test_data/test_one.json")
    assert data.get("age") == 25

    data = read("tests/test_data/test.jsonl")
    assert data.shape[0] == 3
    assert data['age'][0] == 25

    data = read("tests/test_data/test.jsonl", pandas=False)
    assert len(data) == 3
    assert data[0]['age'] == 25

    data = read("tests/test_data/test.jsonl", lines=True, pandas=False)
    # assert len(data) == 3
    # assert data[0]['age'] == 25

def test_read_json():
    data = read("tests/test_data/test.json")
    assert len(data) == 3
    assert data[0]['age'] == 25

    data = read("tests/test_data/test.json", pandas=True)
    assert data.shape[0] == 3
    assert data['age'][0] == 25













