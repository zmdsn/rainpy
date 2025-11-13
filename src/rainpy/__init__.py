# from diskcache import Cache
import pandas as pd
# rain_cache = Cache('./.cache')


from .read import read
from .save import save, write
from .ts import *


def get_imported_names(ignore_list=None):
    """获取从其他模块导入的公共名称"""
    if ignore_list is None:
        ignore_list = []
    
    # 获取所有全局变量
    all_names = set(globals().keys())
    
    # 过滤出公共名称并排除忽略列表
    public_names = [
        name for name in all_names 
        if not name.startswith('_') 
        and name not in ignore_list
        and name not in ['get_imported_names']  # 排除这个函数本身
    ]
    print(public_names)
    return public_names

base_all = ["read", "save", "write"]
imported_names = get_imported_names(ignore_list=base_all)
__all__ = base_all + imported_names
