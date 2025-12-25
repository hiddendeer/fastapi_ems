# SQLAlchemy 2.0+ 异步基本用法指南

## 目录
- [1. 核心概念](#1-核心概念)
- [2. 模型定义](#2-模型定义)
- [3. 异步数据库操作](#3-异步数据库操作)
- [4. 常见查询模式](#4-常见查询模式)
  - [4.1 SELECT 查询](#41-select-查询)
  - [4.2 INSERT 操作](#42-insert-操作)
  - [4.3 UPDATE 操作](#43-update-操作)
  - [4.4 DELETE 操作](#44-delete-操作)
  - [4.5 连表查询（JOIN）](#45-连表查询join) ⭐ **新增**
  - [4.6 事务处理](#46-事务处理)
- [5. 最佳实践](#5-最佳实践)
- [6. 常见错误](#6-常见错误)

---

## 1. 核心概念

### 1.1 异步引擎和会话
```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 创建异步引擎
engine = create_async_engine(
    "mysql+aiomysql://user:password@localhost/dbname",
    echo=True,  # 打印 SQL 语句
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出 pool_size 时最多额外连接数
)

# 创建会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期对象
    autocommit=False,  # 不自动提交
    autoflush=False,  # 不自动 flush
)

# 获取会话
async with async_session() as session:
    # 在这里执行数据库操作
    pass
```

### 1.2 模型基类
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from datetime import datetime

class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass

class User(Base):
    __tablename__ = "users"
    
    # 使用 Mapped 注解进行类型提示
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(),  # 数据库层面的默认值
        nullable=False
    )
```

---

## 2. 模型定义

### 2.1 基础模型
```python
from sqlalchemy import String, Integer, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="商品名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
```

### 2.2 时间戳混入类
```python
class TimestampMixin:
    """为模型添加创建和更新时间戳"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),  # 更新时自动刷新
        nullable=False,
    )

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
```

### 2.3 索引和约束
```python
from sqlalchemy import Index, UniqueConstraint

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    
    # 创建复合索引
    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
        UniqueConstraint("user_id", "order_number", name="uq_user_order"),
    )
```

---

## 3. 异步数据库操作

### 3.1 ⚠️ **关键规则：异步查询必须使用 await**

```python
# ❌ 错误：缺少 await
result = db.execute(select(User).where(User.id == 1)).first()

# ✅ 正确：先 await db.execute()，再调用 first()
result = await db.execute(select(User).where(User.id == 1))
user = result.first()

# ✅ 也可以直接获取单条记录
result = await db.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()  # 返回单个对象或 None
user = result.scalar_one()  # 返回单个对象，找不到则抛异常
```

### 3.2 查询结果提取方法
```python
async def query_examples(db: AsyncSession):
    # 获取单条记录
    result = await db.execute(select(User).where(User.id == 1))
    
    # result.first() - 返回 (obj,) 元组，或 None
    user = result.first()
    if user:
        user_obj = user[0]  # 解包元组
    
    # result.scalar() - 返回第一列的标量值，或 None
    user_id = await db.execute(select(User.id).where(User.username == "john"))
    print(user_id.scalar())  # 返回 1
    
    # result.scalar_one() - 返回唯一的标量值，找不到则抛异常
    user_obj = await db.execute(select(User).where(User.id == 1))
    print(user_obj.scalar_one())  # 返回 User 对象
    
    # result.scalar_one_or_none() - 返回唯一的标量值，或 None
    user_obj = await db.execute(select(User).where(User.username == "john"))
    print(user_obj.scalar_one_or_none())  # 返回 User 对象或 None
    
    # result.all() - 返回所有记录列表
    results = await db.execute(select(User))
    all_users = results.all()  # 返回 [(User1,), (User2,), ...]
    
    # result.scalars() - 返回所有标量值的游标
    results = await db.execute(select(User))
    all_users = results.scalars().all()  # 返回 [User1, User2, ...]
```

---

## 4. 常见查询模式

### 4.1 SELECT 查询
```python
from sqlalchemy import select, and_, or_

async def get_users(db: AsyncSession):
    # 查询所有
    stmt = select(User)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int):
    # 按 ID 查询
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_users_by_status(db: AsyncSession, status: str):
    # 多条件查询
    stmt = select(User).where(
        and_(
            User.is_active == True,
            User.status == status
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def search_users(db: AsyncSession, keyword: str):
    # 模糊查询
    stmt = select(User).where(
        or_(
            User.username.ilike(f"%{keyword}%"),
            User.email.ilike(f"%{keyword}%")
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_users_paginated(db: AsyncSession, offset: int, limit: int):
    # 分页查询
    stmt = select(User).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def count_users(db: AsyncSession):
    # 计数
    from sqlalchemy import func
    stmt = select(func.count(User.id))
    result = await db.execute(stmt)
    return result.scalar()
```

### 4.2 INSERT 操作
```python
async def create_user(db: AsyncSession, user_data: dict):
    # 创建单个对象
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 刷新对象以获取数据库生成的 ID
    return user

async def create_users_bulk(db: AsyncSession, users_data: list[dict]):
    # 批量插入
    users = [User(**data) for data in users_data]
    db.add_all(users)
    await db.commit()
    return users
```

### 4.3 UPDATE 操作
```python
async def update_user(db: AsyncSession, user_id: int, update_data: dict):
    # 方法 1: 对象更新
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
    
    return user

async def update_users_bulk(db: AsyncSession, status: str):
    # 方法 2: SQL 级别批量更新
    from sqlalchemy import update
    stmt = update(User).where(User.is_active == True).values(status=status)
    await db.execute(stmt)
    await db.commit()
```

### 4.4 DELETE 操作
```python
async def delete_user(db: AsyncSession, user_id: int):
    # 方法 1: 对象删除
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await db.delete(user)
        await db.commit()
    
    return user

async def soft_delete_user(db: AsyncSession, user_id: int):
    # 方法 2: 软删除（设置删除标记）
    from sqlalchemy import update
    from datetime import datetime
    
    stmt = update(User).where(User.id == user_id).values(
        deleted_at=datetime.now()
    )
    await db.execute(stmt)
    await db.commit()

async def delete_users_bulk(db: AsyncSession):
    # 批量删除
    from sqlalchemy import delete
    stmt = delete(User).where(User.is_active == False)
    await db.execute(stmt)
    await db.commit()
```

### 4.5 连表查询（JOIN）

```python
from sqlalchemy import and_

# 假设模型定义
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)

# ✅ 内连接（INNER JOIN）- 只返回两表都有匹配的记录
async def get_users_with_posts(db: AsyncSession):
    """获取有文章的所有用户及其文章"""
    stmt = select(User, Post).join(Post, User.id == Post.user_id)
    result = await db.execute(stmt)
    return result.all()  # 返回 [(User1, Post1), (User1, Post2), ...]

# ✅ 左外连接（LEFT OUTER JOIN）- 返回左表所有记录，右表有匹配则包含
async def get_all_users_with_posts(db: AsyncSession):
    """获取所有用户及其文章（用户可能没有文章）"""
    stmt = select(User, Post).outerjoin(Post, User.id == Post.user_id)
    result = await db.execute(stmt)
    return result.all()  # 用户没有文章时 Post 为 None

# ✅ 右外连接（RIGHT OUTER JOIN）- 返回右表所有记录，左表有匹配则包含
async def get_all_posts_with_users(db: AsyncSession):
    """获取所有文章及其作者"""
    stmt = select(Post, User).outerjoin(User, Post.user_id == User.id)
    result = await db.execute(stmt)
    return result.all()

# ✅ 完全连接（FULL OUTER JOIN）- 返回两表所有记录
async def get_all_users_and_posts(db: AsyncSession):
    """获取所有用户和所有文章的完全连接"""
    # 注意：不是所有数据库都支持 FULL OUTER JOIN
    stmt = select(User, Post).outerjoin(Post).select_from(User).union(
        select(User, Post).outerjoin(User).select_from(Post)
    )
    result = await db.execute(stmt)
    return result.all()

# ✅ 多条件 JOIN
async def get_users_with_active_posts(db: AsyncSession):
    """获取所有已发布的文章及其作者（多条件连接）"""
    stmt = select(User, Post).join(
        Post,
        and_(
            User.id == Post.user_id,
            Post.is_published == True  # 多个条件
        )
    )
    result = await db.execute(stmt)
    return result.all()

# ✅ 多表 JOIN
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)

async def get_posts_with_comments_and_users(db: AsyncSession):
    """获取文章、评论和作者信息（三表连接）"""
    stmt = select(Post, Comment, User).join(
        Comment, Post.id == Comment.post_id
    ).join(
        User, Comment.user_id == User.id
    )
    result = await db.execute(stmt)
    return result.all()  # 返回 [(Post1, Comment1, User1), ...]

# ✅ 使用关联关系的隐式 JOIN（推荐）
# 首先在模型中定义关系
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped["User"] = relationship("User", back_populates="posts")

async def get_user_with_posts_eager(db: AsyncSession):
    """使用关系和 selectinload 预加载文章"""
    from sqlalchemy.orm import selectinload
    
    stmt = select(User).options(selectinload(User.posts))
    result = await db.execute(stmt)
    users = result.scalars().unique().all()
    return users  # users[0].posts 已自动加载

# ✅ JOIN with WHERE 条件
async def get_posts_by_author_name(db: AsyncSession, username: str):
    """查询特定作者的所有文章"""
    stmt = select(Post).join(User, User.id == Post.user_id).where(
        User.username == username
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# ✅ JOIN with GROUP BY（聚合查询）
async def get_users_post_count(db: AsyncSession):
    """获取每个用户的文章数"""
    from sqlalchemy import func
    
    stmt = select(
        User.id,
        User.username,
        func.count(Post.id).label("post_count")
    ).outerjoin(Post, User.id == Post.user_id).group_by(User.id, User.username)
    
    result = await db.execute(stmt)
    return result.all()  # [(user_id, username, post_count), ...]

# ✅ JOIN with HAVING 条件（分组后筛选）
async def get_users_with_multiple_posts(db: AsyncSession, min_count: int = 2):
    """获取拥有多于 N 篇文章的用户"""
    from sqlalchemy import func
    
    stmt = select(
        User.id,
        User.username,
        func.count(Post.id).label("post_count")
    ).join(Post, User.id == Post.user_id).group_by(
        User.id, User.username
    ).having(
        func.count(Post.id) >= min_count
    )
    
    result = await db.execute(stmt)
    return result.all()
```

### 4.6 事务处理
```python
async def transfer_money(db: AsyncSession, from_user_id: int, to_user_id: int, amount: float):
    """
    转账示例（包含事务回滚）
    """
    try:
        # 查询用户
        from_user = await db.execute(select(User).where(User.id == from_user_id))
        from_user = from_user.scalar_one_or_none()
        
        to_user = await db.execute(select(User).where(User.id == to_user_id))
        to_user = to_user.scalar_one_or_none()
        
        # 检查余额
        if not from_user or from_user.balance < amount:
            raise ValueError("余额不足")
        
        # 执行转账
        from_user.balance -= amount
        to_user.balance += amount
        
        await db.commit()
        return True
        
    except Exception as e:
        await db.rollback()
        raise e
```

---

## 5. 最佳实践

### 5.1 创建 CRUD 基类
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, Any

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """按 ID 获取记录"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10
    ) -> list[ModelType]:
        """获取多条记录"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """创建记录"""
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """更新记录"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> None:
        """删除记录"""
        await db.delete(db_obj)
        await db.commit()

# 使用示例
user_crud = BaseCRUD(User)
user = await user_crud.get(db, user_id=1)
```

### 5.2 使用依赖注入
```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### 5.3 错误处理
```python
from sqlalchemy.exc import IntegrityError, NoResultFound

async def create_user_safe(db: AsyncSession, user_data: dict):
    try:
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise ValueError("用户名已存在")
    except Exception as e:
        await db.rollback()
        raise e
```

---

## 6. 常见错误

### 6.1 错误：缺少 await
```python
# ❌ 错误
result = db.execute(select(User).where(User.id == 1)).first()
# AttributeError: 'coroutine' object has no attribute 'first'

# ✅ 正确
result = await db.execute(select(User).where(User.id == 1))
user = result.first()
```

### 6.2 错误：混淆同步和异步
```python
# ❌ 错误：使用同步的 sessionmaker
from sqlalchemy.orm import sessionmaker
session_factory = sessionmaker(bind=engine, class_=AsyncSession)

# ✅ 正确：使用异步的 async_sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession)
```

### 6.3 错误：结果集提取
```python
# ❌ 错误：直接使用 result 作为列表
users = await db.execute(select(User))
for user in users:  # 这会迭代 Row 对象
    print(user)

# ✅ 正确：使用 scalars() 或 all()
users = await db.execute(select(User))
for user in users.scalars().all():
    print(user)
```

### 6.4 错误：会话生命周期
```python
# ❌ 错误：会话关闭后访问对象
async with async_session() as session:
    result = await session.execute(select(User))
    user = result.scalar_one_or_none()

# 这里会出错，因为会话已关闭，对象已过期
print(user.username)

# ✅ 正确：在会话内访问或使用 expire_on_commit=False
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 不在提交后过期对象
)
```

### 6.5 错误：N+1 查询问题
```python
# ❌ 低效：N+1 查询
users = await db.execute(select(User))
all_users = users.scalars().all()

for user in all_users:
    # 这会对每个用户执行一次查询
    posts = await db.execute(select(Post).where(Post.user_id == user.id))

# ✅ 高效：使用关联加载
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.posts))
result = await db.execute(stmt)
users = result.scalars().unique().all()
```

---

## 总结对比表

### 基础操作

| 操作 | 正确写法 | 错误写法 |
|------|--------|--------|
| 查询单条 | `await db.execute(...)` | `db.execute(...)` |
| 提取结果 | `result.scalar_one_or_none()` | `result` |
| 查询列表 | `result.scalars().all()` | `result.all()` |
| 创建对象 | `db.add(obj)` + `await db.commit()` | `session.add(obj)` |
| 更新 | `setattr(obj, ...)` + `await db.commit()` | 直接赋值 |
| 批量删除 | `delete(Model).where(...)` | 逐个 `db.delete()` |

### JOIN 操作对比

| JOIN 类型 | 方法 | 说明 | 示例 |
|----------|------|------|------|
| **INNER JOIN** | `.join(Table, condition)` | 返回两表都有匹配的记录 | `select(User, Post).join(Post, User.id == Post.user_id)` |
| **LEFT OUTER JOIN** | `.outerjoin(Table, condition)` | 返回左表所有记录 + 右表匹配 | `select(User, Post).outerjoin(Post, User.id == Post.user_id)` |
| **RIGHT OUTER JOIN** | `.outerjoin(Table, condition)` | 返回右表所有记录 + 左表匹配 | `select(Post, User).outerjoin(User, Post.user_id == User.id)` |
| **关系预加载** | `.options(selectinload(...))` | 自动加载关联数据（推荐） | `select(User).options(selectinload(User.posts))` |
| **多条件 JOIN** | `.join(Table, and_(cond1, cond2))` | 多个连接条件 | `join(Post, and_(User.id == Post.user_id, Post.is_active == True))` |
| **多表 JOIN** | 链式 `.join().join()` | 连接多个表 | `.join(Post).join(Comment)` |

---

## 快速参考：常用 JOIN 示例

```python
# 内连接：只要有关联的记录
select(User, Post).join(Post)

# 左连接：用户全部，文章可能为空
select(User, Post).outerjoin(Post)

# 多条件：AND 条件
select(User, Post).join(Post, and_(User.id == Post.user_id, Post.is_published))

# 聚合：计数
select(User, func.count(Post.id)).outerjoin(Post).group_by(User.id)

# 预加载关系（最佳实践）
select(User).options(selectinload(User.posts))
```

---

**最后提醒：**
- ✅ 在异步 FastAPI 项目中，所有数据库操作都必须使用 `await`！
- ✅ 使用 `selectinload()` 预加载关联数据以避免 N+1 查询问题
- ✅ 复杂连接时优先使用模型关系而非手写 SQL 条件

