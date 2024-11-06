from diskcache import Cache
import pandas as pd
rain_cache = Cache('./.cache')


from .read import read

__all__ = ["read", "write", "save"]
