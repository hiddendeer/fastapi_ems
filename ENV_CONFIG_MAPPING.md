# 环境配置对照表

本文档详细说明 `.env` 文件中的配置项与 `src/config.py` 中类属性的对应关系。

---

## 配置加载流程

```
.env 文件
    ↓
Pydantic BaseSettings
    ↓
src/config.py (Settings 类)
    ↓
FastAPI 应用使用
```

**配置加载优先级**（从高到低）：
1. 环境变量（操作系统级别）
2. `.env` 文件（项目根目录）
3. Python 代码中定义的默认值

---

## 完整配置对照表

### 应用配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `APP_NAME` | `APP_NAME` | `str` | `"FastAPI EMS"` | 应用名称 |
| `APP_VERSION` | `APP_VERSION` | `str` | `"1.0.0"` | 应用版本 |
| `DEBUG` | `DEBUG` | `bool` | `False` | 调试模式（生产环境必须为 `false`） |
| `ENVIRONMENT` | `ENVIRONMENT` | `Environment` | `development` | 运行环境（development/staging/production） |

### API 配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `API_V1_PREFIX` | `API_V1_PREFIX` | `str` | `"/api/v1"` | API 路由前缀 |

### 服务器配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `HOST` | `HOST` | `str` | `"0.0.0.0"` | 服务器绑定地址 |
| `PORT` | `PORT` | `int` | `8000` | 服务器端口 |
| `WORKERS` | `WORKERS` | `int` | `1` | 工作进程数 |

### CORS 配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `CORS_ORIGINS` | `CORS_ORIGINS` | `list[str]` | `["*"]` | 允许的来源（CORS） |
| `CORS_ALLOW_CREDENTIALS` | `CORS_ALLOW_CREDENTIALS` | `bool` | `True` | 是否允许跨域凭证 |
| `CORS_ALLOW_METHODS` | `CORS_ALLOW_METHODS` | `list[str]` | `["*"]` | 允许的 HTTP 方法 |
| `CORS_ALLOW_HEADERS` | `CORS_ALLOW_HEADERS` | `list[str]` | `["*"]` | 允许的请求头 |

### 数据库配置 - 主数据库 ⭐

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `DB_HOST` | `DB_HOST` | `str` | `""` | **数据库服务器地址（必填）** |
| `DB_PORT` | `DB_PORT` | `int` | `3306` | 数据库端口（MySQL 默认值） |
| `DB_USER` | `DB_USER` | `str` | `""` | **数据库用户名（必填）** |
| `DB_PASSWORD` | `DB_PASSWORD` | `str` | `""` | **数据库密码（必填）** |
| `DB_NAME` | `DB_NAME` | `str` | `""` | **默认数据库名（必填）** |
| `DB_ECHO` | `DB_ECHO` | `bool` | `False` | 是否打印 SQL 语句（调试用） |

### 多数据库配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `DB_USER_NAME` | `DB_USER_NAME` | `str` | `"myems_user_db"` | 用户数据库名 |
| `DB_SYSTEM_NAME` | `DB_SYSTEM_NAME` | `str` | `"myems_system_db"` | 系统数据库名 |
| `DB_REPORTING_NAME` | `DB_REPORTING_NAME` | `str` | `"myems_reporting_db"` | 报表数据库名 |

### 数据库连接池配置

| .env 字段 | config.py 属性 | 类型 | 默认值 | 说明 |
|-----------|----------------|------|--------|------|
| `DB_POOL_SIZE` | `DB_POOL_SIZE` | `int` | `10` | 连接池大小（正常连接数） |
| `DB_MAX_OVERFLOW` | `DB_MAX_OVERFLOW` | `int` | `20` | 最大溢出连接数 |
| `DB_POOL_RECYCLE` | `DB_POOL_RECYCLE` | `int` | `1800` | 连接回收时间（秒），防止长时间空闲 |

---

## 配置示例

### .env 文件示例

```ini
# 应用配置
APP_NAME=FastAPI EMS
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# API 配置
API_V1_PREFIX=/api/v1

# 服务器配置
HOST=0.0.0.0
PORT=8000
WORKERS=1

# CORS 配置
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# 数据库配置 - 主数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=myems_db
DB_ECHO=false

# 多数据库配置
DB_USER_NAME=myems_user_db
DB_SYSTEM_NAME=myems_system_db
DB_REPORTING_NAME=myems_reporting_db

# 连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=1800
```

### Python 中使用配置

```python
from src.config import settings

# 访问配置值
print(settings.APP_NAME)  # "FastAPI EMS"
print(settings.DB_HOST)   # "localhost"

# 生成数据库连接 URL
db_url = settings.DATABASE_URL
# mysql+aiomysql://root:your_password@localhost:3306/myems_db?charset=utf8mb4

# 获取配置摘要（安全版本，隐藏敏感信息）
summary = settings.get_config_summary()
print(summary)
# {
#     "app_name": "FastAPI EMS",
#     "database_host": "***",
#     "environment": "development",
#     ...
# }
```

---

## 配置验证规则

### 开发环境（Development）

✅ 允许：
- `DEBUG = true`
- 数据库配置可选

### 生产环境（Production）

❌ 不允许：
- `DEBUG = true` → ❌ 会抛出 `ValueError`
- 缺少必需配置 → ❌ 会抛出 `ValueError`

必需配置：
- `DB_HOST` - 不能为空
- `DB_USER` - 不能为空
- `DB_PASSWORD` - 不能为空
- `DB_NAME` - 不能为空

---

## 环境特定配置

### 本地开发环境

```ini
ENVIRONMENT=development
DEBUG=true
DB_HOST=localhost
DB_POOL_SIZE=5
```

### 测试环境

```ini
ENVIRONMENT=staging
DEBUG=false
DB_HOST=staging-db.internal.com
DB_POOL_SIZE=10
```

### 生产环境

```ini
ENVIRONMENT=production
DEBUG=false
DB_HOST=prod-db.internal.com
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

---

## 常见问题

### Q: 如何覆盖 .env 中的配置？

**A:** 有两种方法：

1. **修改 .env 文件**
   ```ini
   DB_HOST=new_host.com
   ```

2. **使用环境变量**（优先级更高）
   ```bash
   # Linux/Mac
   export DB_HOST=new_host.com
   python -m src.main
   
   # Windows PowerShell
   $env:DB_HOST="new_host.com"
   python -m src.main
   ```

### Q: 配置未被加载怎么办？

**A:** 检查清单：

- [ ] `.env` 文件在项目根目录？
- [ ] 文件名是 `.env`（不是 `.env.local`）？
- [ ] 重启了应用？
- [ ] 字段名称与 config.py 中的属性名一致？（区分大小写）

### Q: 如何检查加载的配置是否正确？

**A:** 在 FastAPI 应用中添加调试端点：

```python
from fastapi import FastAPI
from src.config import settings

app = FastAPI()

@app.get("/config")
def get_config():
    """获取当前配置摘要（仅用于调试）"""
    return settings.get_config_summary()
```

访问 `http://localhost:8000/config` 查看配置。

---

## 相关文件

- `.env` - 本地配置文件（不上传到 Git）
- `.env.example` - 配置示例（上传到 Git）
- `src/config.py` - 配置定义文件
- `SETUP_GUIDE.md` - 环境配置指南

---

最后更新：2025-12-24

