# FastAPI EMS 框架

基于 FastAPI 最佳实践的企业管理系统基础框架，专为快速开展中小型项目设计。

## 🚀 特性

- **模块化架构**：按功能领域组织代码，易于扩展和维护
- **多数据库支持**：支持连接多个 MySQL 数据库
- **FastCRUD 集成**：封装通用 CRUD 操作，减少重复代码
- **异步支持**：全面采用 async/await，提升性能
- **类型安全**：使用 Pydantic 进行数据验证和序列化
- **Docker 支持**：一键部署，开发生产环境统一

## 📁 项目结构

```
fastapi_ems/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── config.py               # 全局配置
│   ├── database.py             # 数据库连接管理
│   ├── models.py               # 全局模型基类
│   ├── schemas.py              # 全局 Pydantic 模型
│   ├── exceptions.py           # 全局异常定义
│   ├── constants.py            # 全局常量
│   ├── pagination.py           # 分页工具
│   ├── middleware.py           # 中间件
│   ├── crud/                   # CRUD 工具封装
│   │   ├── __init__.py
│   │   └── base.py             # 基础 CRUD 类
│   ├── utils/                  # 工具模块
│   │   ├── __init__.py
│   │   └── logger.py           # 日志工具
│   └── demo/                   # 示例模块
│       ├── __init__.py
│       ├── router.py           # 路由定义
│       ├── schemas.py          # Pydantic 模型
│       ├── models.py           # 数据库模型
│       ├── service.py          # 业务逻辑
│       ├── dependencies.py     # 依赖项
│       ├── exceptions.py       # 模块异常
│       └── constants.py        # 模块常量
├── tests/                      # 测试目录
├── requirements/               # 依赖管理
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env                        # 环境配置
├── .env.example                # 配置示例
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # Docker Compose 配置
├── pyproject.toml              # 项目配置
└── README.md
```

## 🔧 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果需要）
cd fastapi_ems

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

主要配置项：

```ini
# 数据库配置
DB_HOST=14.103.138.196
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=py_study

# 应用配置
DEBUG=true
ENVIRONMENT=development
```

### 3. 启动应用

```bash
# 开发模式（带热重载）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m src.main
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker 部署

### 开发环境

```bash
# 启动开发环境（带热重载）
docker-compose --profile dev up app-dev
```

### 生产环境

```bash
# 构建并启动
docker-compose up -d app

# 查看日志
docker-compose logs -f app
```

## 📚 核心概念

### 1. 模块结构

每个业务模块应包含以下文件：

| 文件 | 用途 |
|------|------|
| `router.py` | 路由定义，所有 API 端点 |
| `schemas.py` | Pydantic 模型，请求/响应数据结构 |
| `models.py` | SQLAlchemy 模型，数据库表定义 |
| `service.py` | 业务逻辑层 |
| `dependencies.py` | FastAPI 依赖项 |
| `exceptions.py` | 模块特定异常 |
| `constants.py` | 模块常量 |

### 2. 数据库操作

#### 使用 BaseCRUD

```python
from src.crud import BaseCRUD
from src.demo.models import Item
from src.demo.schemas import ItemCreate, ItemUpdate

class ItemCRUD(BaseCRUD[Item, ItemCreate, ItemUpdate]):
    pass

item_crud = ItemCRUD(Item)

# 基本操作
item = await item_crud.get(db, id=1)
items = await item_crud.get_multi(db, offset=0, limit=10)
new_item = await item_crud.create(db, object=item_data)
await item_crud.update(db, object=update_data, id=1)
await item_crud.delete(db, id=1)
```

#### 多数据库支持

```python
from src.database import get_db_dependency

# 创建指定数据库的依赖
get_user_db = get_db_dependency("myems_user_db")

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_user_db)):
    # 使用 myems_user_db 数据库
    ...
```

### 3. 依赖注入

#### 参数自动匹配原理

FastAPI 的依赖注入会**自动按名称匹配参数**：

```python
# 路由定义
@router.get("/items/{item_id}")                    # ← URL 路径中有 item_id
async def get_item(
    item: dict = Depends(valid_item_id),          # ← 使用依赖
) -> ItemResponse:
    return ItemResponse(**item)


# 依赖函数
async def valid_item_id(
    item_id: int,                                 # ← 参数名必须是 item_id（与路由路径匹配）
    db: AsyncSession = Depends(get_db),           # ← 递归依赖
) -> dict:
    item = await service.get_item_by_id(db, item_id)
    if not item:
        raise NotFoundException(f"Item {item_id} 不存在")
    return item
```

**自动工作流程**：
```
请求: GET /items/1
  ↓
FastAPI 提取 item_id=1 从 URL
  ↓
FastAPI 看到路由需要 Depends(valid_item_id)
  ↓
FastAPI 检查 valid_item_id 的参数
  ↓
自动匹配：item_id → 从 URL 获取
         db → 从 get_db() 依赖获取
  ↓
调用: valid_item_id(item_id=1, db=<session>)
  ↓
验证通过，返回 item 字典给路由
```

#### 关键点

✅ **参数名称必须匹配** - `{item_id}` 路径参数对应 `item_id` 函数参数  
✅ **自动注入** - 无需显式传递，FastAPI 自动处理  
✅ **链式依赖** - 依赖函数可以依赖其他依赖  
✅ **缓存** - 同一请求中，相同依赖只执行一次  

#### 多个依赖示例

```python
# 验证用户是否是 admin（基于用户验证）
async def valid_admin_user(
    user: dict = Depends(get_current_user),  # ← 链式依赖
) -> dict:
    if user["role"] != "admin":
        raise ForbiddenException("需要 admin 权限")
    return user


# 使用链式依赖
@router.delete("/items/{item_id}")
async def delete_item(
    admin: dict = Depends(valid_admin_user),        # ← 自动验证权限
    item: dict = Depends(valid_item_id),            # ← 自动验证资源
) -> MessageResponse:
    """只有 admin 可以删除 Item"""
    return MessageResponse(message="删除成功")
```

### 4. 异常处理

```python
from src.exceptions import NotFoundException, BadRequestException

# 使用全局异常
raise NotFoundException("资源不存在")
raise BadRequestException("请求参数错误")

# 定义模块异常
class ItemNotFound(NotFoundException):
    def __init__(self, item_id: int):
        super().__init__(f"Item {item_id} 不存在")
```

### 5. 分页

```python
from src.pagination import get_pagination, PaginationParams

@router.get("/items")
async def list_items(
    pagination: PaginationParams = Depends(get_pagination),
):
    offset = (pagination.page - 1) * pagination.page_size
    # 使用 offset 和 pagination.page_size 查询
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_health.py

# 带覆盖率报告
pytest --cov=src --cov-report=html
```

## 📝 代码规范

使用 Ruff 进行代码检查和格式化：

```bash
# 检查代码
ruff check src

# 自动修复
ruff check --fix src

# 格式化代码
ruff format src
```

## 🔌 添加新模块

1. 在 `src/` 下创建新模块目录
2. 创建必要的文件（router.py, schemas.py, models.py 等）
3. 在 `src/main.py` 中注册路由

```python
# src/main.py
from src.your_module.router import router as your_router

app.include_router(your_router, prefix=settings.API_V1_PREFIX)
```

## 📊 数据库迁移（可选）

如需使用 Alembic 进行数据库迁移：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 🔗 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [FastCRUD 文档](https://github.com/benavlabs/fastcrud)

## 📄 许可证

MIT License

