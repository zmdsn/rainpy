# `logger` 使用手册

> **一句话定位**：  
> 一个轻量、灵活、生产就绪的 Python 日志工具，支持控制台、文件轮转、Loki 推送，一行代码搞定日志配置。

---

## 📦 安装

### 基础功能（控制台 + 文件日志）
无需额外依赖，Python 标准库自带。

### Loki 支持（可选）
```bash
pip install loki-handler
```

---

## 🚀 快速上手

### 步骤 1：导入模块
```python
from smart_logger import set_logger
```

### 步骤 2：初始化 Logger
```python
logger = set_logger(
    name="myapp",
    level="INFO",
    outputs=["stdout", "file"]
)
```

### 步骤 3：开始记录
```python
logger.info("服务启动成功")
logger.error("数据库连接失败")
```

✅ 输出示例（控制台）：
```
2026-01-15 14:30:00 [PID:12345] [INFO] myapp: 服务启动成功
2026-01-15 14:30:01 [PID:12345] [ERROR] myapp: 数据库连接失败
```

---

## 🧩 核心功能

| 功能 | 说明 |
|------|------|
| ✅ **多输出目标** | 同时输出到控制台、文件、Loki |
| ✅ **自动 PID 标记** | 每条日志包含进程 ID，便于多进程排查 |
| ✅ **智能日志轮转** | 按时间（天/小时）或按大小（MB）自动分割 |
| ✅ **Loki 一键集成** | 自动补全 URL，标签可自定义 |
| ✅ **防重复 Handler** | 多次调用不会导致日志重复输出 |
| ✅ **字符串级别支持** | 直接使用 `"INFO"` 而非 `logging.INFO` |

---

## 🛠️ 配置指南

### 1. 选择输出目标 (`outputs`)
| 值 | 效果 |
|----|------|
| `["stdout"]` | 仅输出到控制台（默认） |
| `["file"]` | 仅写入文件（路径由 `log_dir` 指定） |
| `["stdout", "file"]` | 同时输出到控制台和文件 |
| `["loki"]` | 仅推送到 Loki（需安装 `loki-handler`） |
| `["stdout", "loki"]` | 控制台 + Loki（推荐生产环境） |

### 2. 文件轮转策略

#### 按时间轮转（推荐 Web 服务）
```python
set_logger(
    outputs=["file"],
    rotation_type="time",
    when="midnight",   # 每天午夜轮转
    interval=1,
    backup_count=30    # 保留30天日志
)
```

#### 按大小轮转（推荐批处理任务）
```python
set_logger(
    outputs=["file"],
    rotation_type="size",
    max_bytes=50 * 1024 * 1024,  # 50MB
    backup_count=10               # 保留10个文件
)
```

### 3. Loki 集成

```python
set_logger(
    outputs=["loki"],
    loki_url="http://loki.prod:3100",      # 自动补全为 /loki/api/v1/push
    loki_tags={
        "env": "production",
        "service": "order-service"
    }
)
```

> 💡 **提示**：即使未安装 `loki-handler`，程序也不会崩溃，仅打印警告。

---

## 📝 日志级别说明

| 级别 | 使用场景 | 数值 |
|------|--------|-----|
| `DEBUG` | 详细调试信息（开发环境） | 10 |
| `INFO` | 常规运行信息（如“服务启动”） | 20 |
| `WARNING` | 潜在问题（如“磁盘空间不足”） | 30 |
| `ERROR` | 错误事件（但服务仍可运行） | 40 |
| `CRITICAL` | 严重错误（可能导致服务中断） | 50 |

**设置建议**：
- 开发环境：`level="DEBUG"`
- 生产环境：`level="INFO"` 或 `"WARNING"`

---

## 🌰 典型场景配置

### 场景 1：Web API 服务（生产环境）
```python
logger = set_logger(
    name="api-gateway",
    level="INFO",
    outputs=["stdout", "loki"],
    loki_url="http://loki.internal:3100",
    loki_tags={"team": "backend", "env": "prod"}
)
```

### 场景 2：数据批处理脚本
```python
logger = set_logger(
    name="daily-report",
    level="DEBUG",
    outputs=["file"],
    log_dir="/data/logs/reports",
    rotation_type="size",
    max_bytes=100 * 1024 * 1024,  # 100MB
    backup_count=5
)
```

### 场景 3：本地开发调试
```python
logger = set_logger(
    name="dev-test",
    level="DEBUG",
    outputs=["stdout"]
)
```

---

## ⚠️ 常见问题解决

### Q1: 日志没有写入文件？
- **检查目录权限**：确保应用对 `log_dir` 有写权限
- **确认 outputs 包含 "file"**
- **查看是否被其他日志框架干扰**（如 Flask 内置 logger）

### Q2: Loki 推送失败？
- 确认已安装：`pip install loki-handler`
- 测试 URL 可达性：`curl http://your-loki:3100/ready`
- 检查防火墙/网络策略

### Q3: 为什么日志重复输出？
- 本模块已自动清理旧 handlers，通常不会发生
- **避免**在循环中多次调用 `set_logger()`

### Q4: 如何在 Docker 中使用？
- 推荐 `outputs=["stdout"]`，由 Docker 收集日志
- 或挂载卷：`-v /host/logs:/app/logs`

---

## 🔒 安全与合规

- **不记录敏感信息**：本模块不处理日志内容，需开发者自行脱敏
- **日志保留策略**：通过 `backup_count` 控制磁盘占用
- **多租户隔离**：不同服务使用不同 `name`，日志文件自动分离

---

## 📊 性能说明

| 输出方式 | 性能影响 | 适用场景 |
|---------|--------|--------|
| `stdout` | 极低 | 所有场景（尤其容器化） |
| `file`（时间轮转） | 低 | Web 服务、长运行进程 |
| `file`（大小轮转） | 低 | 高吞吐批处理 |
| `loki` | 中（网络 I/O） | 集中式日志系统 |

> 💡 **建议**：高并发场景避免同时开启文件 + Loki，优先选择 stdout + 外部收集器。

---

## 📜 版本兼容性

| Python 版本 | 支持情况 |
|------------|--------|
| ≥ 3.8 | ✅ 完全支持 |
| 3.7 | ⚠️ 基本功能可用（`Literal` 类型需降级） |
|  ✅ **总结**：  
> **`set_logger()` 一行代码，解决 90% 的日志需求。**  
> 从本地开发到云原生生产环境，无缝适配。

---

**附：完整参数速查表**

| 参数 | 默认值 | 必填 | 说明 |
|------|-------|-----|------|
| `name` | `"app"` | 否 | Logger 名称 |
| `level` | `"DEBUG"` | 否 | 日志级别 |
| `outputs` | `["stdout"]` | 否 | 输出目标列表 |
| `log_dir` | `"./logs"` | 否 | 文件日志目录 |
| `rotation_type` | `"time"` | 否 | 轮转类型 |
| `when` | `"midnight"` | 否 | 时间轮转单位 |
| `interval` | `1` | 否 | 轮转间隔 |
| `max_bytes` | `10MB` | 否 | 文件大小上限 |
| `backup_count` | `15` | 否 | 保留文件数 |
| `loki_url` | `"http://localhost:3100"` | 否 | Loki 地址 |
| `loki_tags` | `{"application": name}` | 否 | Loki 标签 |