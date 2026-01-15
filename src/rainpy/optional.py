import importlib
from typing import Optional, Callable

def optional_import(
    module_name: str,
    package_name: str = None,
    error_msg: str = None
) -> tuple[Optional[object], Callable[[], None]]:
    """
    可选导入模块，失败时返回 (None, 提示函数)
    
    参数：
        module_name: 要导入的模块名（如 "pandas"）
        package_name: 对应的 pip 包名（默认同 module_name）
        error_msg: 自定义错误提示
    
    返回：
        (模块对象/None, 提示函数)
    """
    if package_name is None:
        package_name = module_name
    
    if error_msg is None:
        error_msg = f"请安装可选依赖：uv pip install myutils[excel]"  # 可动态适配
    
    try:
        # 尝试导入模块
        module = importlib.import_module(module_name)
        return module, lambda: None  # 导入成功，提示函数为空
    except ImportError:
        # 导入失败，返回 None 和提示函数
        def hint():
            raise ImportError(error_msg)
        return None, hint
