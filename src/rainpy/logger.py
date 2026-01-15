# smart_logger.py
import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import List, Optional, Literal, Union
from urllib.parse import urljoin
# 尝试导入 LokiHandler
try:
    from loki_handler import LokiHandler
except ImportError:
    LokiHandler = None


from .optional import optional_import

pandas, pandas_hint = optional_import(
    module_name="pandas",
    package_name="pandas",
    error_msg="Excel 功能需要安装可选依赖：uv pip install rainpy[]"
)


def _parse_log_level(level: Union[str, int]) -> int:
    """
    将日志级别字符串（如 'INFO'）或整数转换为标准 logging 级别整数。
    支持: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    """
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        level = level.upper()
        # 使用 logging 内置映射（兼容且安全）
        known_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "WARN": logging.WARNING,  # 兼容 WARN
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if level not in known_levels:
            raise ValueError(
                f"Invalid log level: {level}. "
                f"Expected one of: {list(known_levels.keys())}"
            )
        return known_levels[level]
    raise TypeError(f"Log level must be str or int, got {type(level)}")


def set_logger(
    name: str = "app",
    level: Union[str, int] = logging.DEBUG,  # ← 改为字符串默认
    outputs: Optional[List[str]] = None,
    # 文件日志配置
    log_dir: str = "./logs",
    rotation_type: Literal["time", "size"] = "time",
    when: str = "midnight",
    interval: int = 1,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 15,
    # Loki 配置
    loki_url: str = "http://localhost:3100",
    loki_tags: Optional[dict] = None,
) -> logging.Logger:
    """
    一个灵活、带 PID、支持多输出的日志记录器。
    Args:
        name: logger 名称
        level: 日志级别，可为字符串（如 "INFO"）或整数（如 logging.INFO）
        outputs: 输出目标列表，如 ['stdout', 'file', 'loki']（默认 ['stdout']）
        ...（其他参数同前）
    """
    if outputs is None:
        outputs = ["stdout"]

    # 解析日志级别
    log_level = _parse_log_level(level)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 防止重复 handlers
    if logger.handlers:
        logger.handlers.clear()

    # 格式包含 PID
    formatter = logging.Formatter(
        fmt="%(asctime)s [PID:%(process)d] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # === stdout ===
    if "stdout" in outputs:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # === file ===
    if "file" in outputs:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}.log")

        if rotation_type == "time":
            handler = TimedRotatingFileHandler(
                filename=log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding="utf-8",
            )
        elif rotation_type == "size":
            handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
        else:
            raise ValueError("rotation_type must be 'time' or 'size'")
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # === loki ===
    if "loki" in outputs:
        if LokiHandler is None:
            logger.warning(
                "Loki output requested but 'loki-handler' is not installed. "
                "Run: pip install loki-handler"
            )
        else:
            loki_url = loki_url.rstrip("/")
            if not loki_url.endswith("/loki/api/v1/push"):
                loki_url += "/loki/api/v1/push"
            tags = loki_tags or {"application": name}
            handler = LokiHandler(url=loki_url, tags=tags, version="1")
            handler.setLevel(log_level)
            logger.addHandler(handler)

    return logger