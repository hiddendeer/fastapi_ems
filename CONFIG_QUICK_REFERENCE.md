# 配置快速参考卡

快速查看 `.env` 文件与 `src/config.py` 的映射关系

---

## 📋 配置字段速查表

### 🔴 必填字段（生产环境）

```
DB_HOST         → settings.DB_HOST          # 数据库服务器地址
DB_USER         → settings.DB_USER          # 数据库用户名
DB_PASSWORD     → settings.DB_PASSWORD      # 数据库密码
DB_NAME         → settings.DB_NAME          # 默认数据库名
```

### 🟡 重要配置

```
DEBUG           → settings.DEBUG            # 调试模式（生产必须false）
ENVIRONMENT     → settings.ENVIRONMENT      # 运行环境
DB_PORT         → settings.DB_PORT          # 数据库端口（默认3306）
```

### 🟢 可选配置

```
APP_NAME        → settings.APP_NAME         # 默认："FastAPI EMS"
APP_VERSION     → settings.APP_VERSION      # 默认："1.0.0"
HOST            → settings.HOST             # 默认："0.0.0.0"
PORT            → settings.PORT             # 默认：8000
API_V1_PREFIX   → settings.API_V1_PREFIX    # 默认："/api/v1"
DB_ECHO         → settings.DB_ECHO          # 默认：False
DB_POOL_SIZE    → settings.DB_POOL_SIZE     # 默认：10
```

---

## 🚀 快速开始

### 1️⃣ 本地开发

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入数据库信息
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=myems_db

# 启动应用
uvicorn src.main:app --reload
```

### 2️⃣ 检查配置是否加载

```python
from src.config import settings

# 验证配置
print(settings.DB_HOST)      # 应该打印你的主机名
print(settings.ENVIRONMENT)  # 应该打印 development

# 获取配置摘要（安全版本）
print(settings.get_config_summary())
```

### 3️⃣ 生产部署

```bash
# 设置环境变量
export DB_HOST=prod-db.com
export DB_USER=prod_user
export DB_PASSWORD=secure_password
export ENVIRONMENT=production
export DEBUG=false

# 启动应用
python -m uvicorn src.main:app
```

---

## 📊 配置加载流程

```
优先级从高到低：
┌──────────────────────────────────────┐
│  1️⃣ 环境变量（操作系统）               │
│     export DB_HOST=server.com         │
└──────────────────────────────────────┘
              ↓（如果未设置）
┌──────────────────────────────────────┐
│  2️⃣ .env 文件（项目根目录）           │
│     DB_HOST=localhost                 │
└──────────────────────────────────────┘
              ↓（如果未设置）
┌──────────────────────────────────────┐
│  3️⃣ config.py 中的默认值              │
│     DB_HOST: str = ""                 │
└──────────────────────────────────────┘
```

**示例**：如果同时设置了环境变量和 `.env` 中的值，优先使用环境变量。

---

## ✅ 配置检查清单

部署前验证：

- [ ] `.env` 文件存在且在项目根目录
- [ ] `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` 都已填写
- [ ] 生产环境：`DEBUG=false`，`ENVIRONMENT=production`
- [ ] 生产环境：`DB_PASSWORD` 使用强密码
- [ ] 数据库服务器可访问且允许连接
- [ ] `.env` 文件在 `.gitignore` 中（不会上传到 Git）

---

## 🔧 常见命令

### 查看当前配置

```python
# 在应用中添加调试端点
from src.config import settings

@app.get("/config/debug")
def get_config():
    return settings.get_config_summary()

# 访问：http://localhost:8000/config/debug
```

### 验证 .env 文件

```bash
# Windows
type .env

# Linux/Mac
cat .env
```

### 检查配置是否生效

```bash
# 运行以下命令，查看是否连接成功
python -c "from src.config import settings; print(settings.get_config_summary())"
```

---

## 🚨 常见问题速解

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `FileNotFoundError: .env` | `.env` 文件不存在 | `cp .env.example .env` |
| `无法连接数据库` | 数据库信息错误 | 检查 `DB_HOST`, `DB_USER`, `DB_PASSWORD` |
| 配置未改变 | 应用未重启 | 停止（Ctrl+C）然后重启应用 |
| 优先级冲突 | 环境变量覆盖 `.env` | 检查是否设置了环境变量 |

---

## 📚 详细文档

- **详细配置说明**：见 `ENV_CONFIG_MAPPING.md`
- **环境配置指南**：见 `SETUP_GUIDE.md`
- **完整代码注释**：见 `src/config.py`

---

## 🔐 安全提示

❌ **不要做的事**：
- 提交 `.env` 文件到 Git
- 在代码中硬编码密码
- 在日志中打印敏感信息
- 将密码写在注释中

✅ **应该做的事**：
- 使用 `.env` 文件管理敏感配置
- 定期更换数据库密码
- 使用强密码（12+ 字符，含大小写、数字、特殊字符）
- 为不同环境使用不同的凭证

---

**最后更新**：2025-12-24  
**版本**：FastAPI EMS 1.0.0

