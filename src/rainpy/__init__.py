from diskcache import Cache
import pandas as pd
rain_cache = Cache('./.cache')


from .read import read
from .save import save, write

__all__ = ["read", "save", "write"]
