# 环境配置指南

本文档说明如何正确配置敏感信息（如数据库凭证）而不会泄露到版本控制系统。

## 重要提示 ⚠️

**永远不要将以下信息提交到GitHub：**
- 数据库密码
- API密钥和令牌
- 个人访问令牌
- 数据库主机名（如果包含内网信息）
- 任何其他敏感凭证

---

## 快速开始

### 1. 复制环境配置模板

```bash
cp .env.example .env
```

### 2. 编辑 `.env` 文件

在项目根目录创建或编辑 `.env` 文件，填入实际的数据库凭证：

```ini
# 数据库配置
DB_HOST=your_actual_database_host
DB_PORT=3306
DB_USER=your_actual_database_user
DB_PASSWORD=your_actual_database_password
DB_NAME=your_actual_database_name
```

### 3. 验证配置

- ✅ 本地的 `.env` 文件包含真实凭证
- ✅ `.env` 文件在 `.gitignore` 中，不会被提交
- ✅ `.env.example` 只包含示例值，可安全提交

---

## 文件说明

### `.env` （本地配置，不上传）
```
.env                    ← 你的本地配置文件（包含真实凭证）
                        ← 该文件被 .gitignore 忽略，不会提交到GitHub
```

**不要编辑或提交此文件！**

### `.env.example` （模板文件，上传到GitHub）
```
.env.example           ← 配置模板（仅包含示例值）
                       ← 该文件被上传到GitHub，供其他开发者参考
```

**这是配置示例，所有真实数据都被替换为占位符。**

---

## 配置字段详解

### 必需配置

| 字段 | 说明 | 示例 |
|------|------|------|
| `DB_HOST` | 数据库服务器地址 | `192.168.1.100` 或 `db.example.com` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_USER` | 数据库用户名 | `admin` |
| `DB_PASSWORD` | 数据库密码 | `your_secure_password` |
| `DB_NAME` | 默认数据库名 | `myems_db` |

### 可选配置

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `false` | 调试模式（生产环境必须关闭） |
| `ENVIRONMENT` | `development` | 运行环境（development/staging/production） |
| `DB_ECHO` | `false` | 是否打印SQL语句（调试用） |
| `DB_POOL_SIZE` | `10` | 数据库连接池大小 |

---

## 本地开发流程

### 第一次配置

```bash
# 1. 克隆项目
git clone https://github.com/hiddendeer/fastapi_ems.git
cd fastapi_ems

# 2. 复制配置模板
cp .env.example .env

# 3. 编辑 .env，填入你的数据库信息
# 在编辑器中打开 .env 文件
# 将占位符替换为实际的数据库凭证

# 4. 验证配置是否正确
# 运行应用，检查数据库连接是否成功
```

### 日常开发

```bash
# 启动应用
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 应用会自动从 .env 文件加载配置
```

---

## 配置优先级

FastAPI配置加载的优先级（从高到低）：

1. **环境变量** - 操作系统的环境变量（最高优先级）
2. **`.env` 文件** - 项目根目录的 `.env` 文件
3. **默认值** - 代码中定义的默认值（最低优先级）

**示例：** 如果同时设置了环境变量 `DB_HOST=prod-server` 和 `.env` 中的 `DB_HOST=dev-server`，则会使用环境变量的值。

---

## Docker 部署

### 使用环境变量（推荐）

```bash
# 启动容器时传入环境变量
docker run -e DB_HOST=db.example.com \
           -e DB_USER=admin \
           -e DB_PASSWORD=secret \
           -e DB_NAME=myems_db \
           -p 8000:8000 \
           fastapi-ems:latest
```

### 使用 Docker Compose

创建 `.env` 文件后：

```bash
docker-compose up -d
```

Docker Compose 会自动加载 `.env` 文件中的变量。

---

## 安全最佳实践

### ✅ 应该做的事

- ✅ 在 `.gitignore` 中包含 `.env` 和所有 `.env.*.local` 文件
- ✅ 定期更换数据库密码
- ✅ 为不同环境使用不同的凭证
- ✅ 使用强密码（至少12个字符，含大小写字母、数字、特殊字符）
- ✅ 将 `.env.example` 提交到版本控制，作为配置参考

### ❌ 千万别做的事

- ❌ 不要将 `.env` 文件提交到GitHub
- ❌ 不要在代码注释中写入密码
- ❌ 不要在公开的地方分享 `.env` 文件
- ❌ 不要在日志中打印密码
- ❌ 不要将敏感信息硬编码在源代码中

---

## 检查清单

提交代码前，确保：

- [ ] `.env` 文件不在暂存区（运行 `git status` 检查）
- [ ] 所有敏感信息都在 `.env` 文件中，而不是代码中
- [ ] `.env.example` 只包含示例值，没有真实凭证
- [ ] `.gitignore` 包含 `.env` 规则

---

## 故障排除

### 应用无法连接数据库

**问题：** `Fatal: unable to access database`

**解决步骤：**

1. 检查 `.env` 文件是否存在
2. 验证数据库凭证是否正确
3. 确认数据库服务器是否运行且可访问
4. 检查防火墙是否允许数据库连接

```bash
# 测试数据库连接
# Windows
mysql -h 你的DB_HOST -u 你的DB_USER -p
# 然后输入密码
```

### 环境变量未被加载

**问题：** 应用仍使用默认值而不是 `.env` 中的值

**原因：**
- `.env` 文件名不正确（应为 `.env`，不是 `.env.local`）
- `.env` 文件不在项目根目录
- 应用未重启

**解决方案：**
```bash
# 确保 .env 文件在项目根目录
ls -la .env

# 重启应用
# 停止当前运行的应用（Ctrl+C）
# 重新启动应用
```

---

## 相关文件

- `src/config.py` - 配置定义
- `.env.example` - 配置模板（安全版本）
- `.gitignore` - Git忽略规则

---

## 参考资源

- [Pydantic BaseSettings文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Python dotenv库](https://python-dotenv.readthedocs.io/)
- [12 Factor App - 配置最佳实践](https://12factor.net/config)

---

最后更新：2025-12-24

