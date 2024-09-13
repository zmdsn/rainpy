import pytest
from rainpy.raindrop import make_frame

from collections import namedtuple

def test_raindrop():
    drops = {"name": "example", 
                "floder": "./example", 
                "author": "zmdsn",
                "email":"zmdsn@126.com",
                "url":"https://github.com/zmdsn/rainpy"}
    RainDrop = namedtuple("RainDrop", drops.keys())
    drop = RainDrop(**drops)
