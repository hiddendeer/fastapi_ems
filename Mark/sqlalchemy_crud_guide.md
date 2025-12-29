# SQLAlchemy ORM CRUD 核心用法指南

本指南基于 FastAPI + SQLAlchemy 2.0 现代异步模式，结合项目中使用的 `FastCRUD` 设计思想，为你总结最实用的数据库操作方法。

---

## 1. 核心概念：ORM vs 原生 SQL
- **ORM (Object-Relational Mapping)**: 将数据库表映射为 Python 类。优势是类型安全、代码简洁、易于维护。
- **FastCRUD**: 本项目使用的第三方库，它进一步封装了 SQLAlchemy，让你通过简单的函数调用（如 `crud.get`）代替繁琐的 `select(...).where(...)`。

---

## 2. 基础 CRUD 操作 (ORM 风格)

### C - Create (创建)
在现代异步 SQLAlchemy 中，创建一条记录通常涉及：实例化模型 -> 添加到 session -> 提交。

```python
# 1. 纯 ORM 写法
new_user = User(nickname="小明", email="xiaoming@example.com")
db.add(new_user)
await db.commit()
await db.refresh(new_user) # 刷新以获取数据库生成的 ID

# 2. FastCRUD / BaseCRUD 封装写法 (推荐)
# 内部自动处理了 model_dump 和 commit
new_user = await user_crud.create(db, UserCreate(nickname="小明"))
```

### R - Read (读取)

#### 获取单条 (Get)
```python
# 1. 纯 ORM 写法
from sqlalchemy import select
stmt = select(User).where(User.id == 1)
result = await db.execute(stmt)
user = result.scalar_one_or_none()

# 2. FastCRUD 封装写法 (极简)
user = await user_crud.get(db, id=1)
# 支持高级筛选
user = await user_crud.get(db, nickname="小明", status=1)
```

#### 获取列表 (Get Multi)
```python
# FastCRUD 封装写法：支持分页和排序
result = await user_crud.get_multi(
    db, 
    offset=0, 
    limit=10, 
    sort_columns="created_at", 
    sort_orders="desc"
)
# 返回: {"data": [user1, user2...], "total_count": 100}
```

### U - Update (更新)
更新时，推荐使用“先查后改”或“直接条件更新”。

```python
# 1. 先查后改 (适合复杂逻辑)
user = await db.get(User, 1)
user.nickname = "新昵称"
await db.commit()

# 2. 条件更新 (FastCRUD 写法 - 推荐)
await user_crud.update(db, {"nickname": "新昵称"}, id=1)
```

### D - Delete (删除)
区分**硬删除**（物理删除）和**软删除**（标记删除）。

```python
# 1. 物理删除 (从硬盘抹除)
await user_crud.delete(db, id=1)

# 2. 软删除 (推荐：项目中通常配置了 deleted_at 字段)
# 将 deleted_at 设置为当前时间，数据还在。
# FastCRUD 结合项目中 BaseModel 的逻辑会自动处理。
await user_crud.delete(db, id=1, soft_delete=True)
```

---

## 3. 进阶技巧 (老手必备)

### 3.1 高级筛选 (Magic Filters)
`FastCRUD` 支持在参数后追加操作符：
- `age__gt=18`: 大于 (Greater Than)
- `name__like="%张%"`: 模糊查询
- `status__in=[1, 2]`: 在范围内

```python
# 示例：查找年龄大于 18 且状态在 [1, 2] 中的用户
users = await user_crud.get_multi(db, age__gt=18, status__in=[1, 2])
```

### 3.2 批量创建 (Performance Boost)
当你需要插入 1000 条数据时，千万不要用循环调 `create`。
```python
# BaseCRUD 中封装的优化版演示
users_to_create = [UserCreate(nickname=f"用户{i}") for i in range(100)]
await user_crud.create_many(db, users_to_create)
```

### 3.3 关联查询 (Join)
当需要跨表获取数据时（例如：获取用户及其关联的任务）：
```python
# FastCRUD 提供了便捷的 get_joined
result = await user_crud.get_multi_joined(
    db,
    join_model=Task,
    join_prefix="task_",
    join_on=User.id == Task.user_id
)
```

---

## 4. 学习建议
1.  **先懂原理**：理解 `select` 和 `stmt` 的构建，因为复杂的统计查询终究要写原生或 ORM 语句。
2.  **善用工具**：日常简单的增删改查，直接用 `BaseCRUD` 封装好的方法，不仅代码整洁，还能避免忘记 `commit` 的低级错误。
3.  **关注性能**：大量数据用 `create_many`，查询只要特定字段用 `schema_to_select` 减少 IO。

> [!TIP]
> 以后在读项目代码时，只要看到 `await xxx_crud.get(...)` 就可以联想到它背后是在拼凑一条高效的 SQL 并异步执行。
