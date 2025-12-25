# FastAPI 请求体（Request Body）完全指南

## 基础概念

FastAPI 会自动根据参数类型注解将 JSON 请求体转换为 Python 对象。

---

## 1️⃣ 简单对象

### 场景：接收单个对象

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@router.post("/items")
async def create_item(item: Item):
    """接收单个 Item 对象"""
    return item

# 请求示例：
# POST /items
# Content-Type: application/json
# {
#   "name": "苹果",
#   "price": 9.99
# }
```

---

## 2️⃣ 数组/列表对象

### 场景：接收多个对象（最常用）

```python
class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@router.post("/items/batch")
async def batch_create(items: list[Item]):
    """接收 Item 对象数组"""
    return {"count": len(items), "items": items}

# 请求示例：
# POST /items/batch
# Content-Type: application/json
# [
#   {"name": "苹果", "price": 9.99, "description": "红苹果"},
#   {"name": "香蕉", "price": 5.99}
# ]

# 响应：
# {"count": 2, "items": [...]}
```

---

## 3️⃣ 带命名的对象数组（最常见的场景）

### 场景：前端传 `{ "items": [{}] }` 或 `{ "data": [{}] }` 格式

#### 方式 1：创建包装 Schema

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

class ItemListRequest(BaseModel):
    """包装请求体"""
    items: list[Item]  # 或 data: list[Item]

@router.post("/batch")
async def batch_add_items(request: ItemListRequest):
    """接收命名的项目列表"""
    items = request.items
    print(f"接收 {len(items)} 条数据")
    return {"message": f"成功接收 {len(items)} 条数据"}

# 请求示例：
# POST /batch
# {
#   "items": [
#     {"name": "Item 1", "price": 10.0},
#     {"name": "Item 2", "price": 20.0}
#   ]
# }
```

#### 方式 2：使用 Body 显式指定

```python
from fastapi import Body

@router.post("/batch")
async def batch_add_items(items: list[Item] = Body(...)):
    """使用 Body(...) 显式指定请求体"""
    return {"count": len(items)}

# 请求示例（直接数组）：
# POST /batch
# [
#   {"name": "Item 1", "price": 10.0},
#   {"name": "Item 2", "price": 20.0}
# ]
```

#### 方式 3：使用 embed 参数（推荐）

```python
from fastapi import Body

@router.post("/batch")
async def batch_add_items(items: list[Item] = Body(..., embed=True)):
    """使用 embed=True 自动生成包装体"""
    return {"count": len(items)}

# 请求示例：
# POST /batch
# {
#   "items": [
#     {"name": "Item 1", "price": 10.0},
#     {"name": "Item 2", "price": 20.0}
#   ]
# }
```

---

## 4️⃣ 自定义字段名称

### 场景：前端使用不同的字段名（如 `add_data`）

```python
from pydantic import BaseModel, Field

class ItemListRequest(BaseModel):
    # 使用 Field 自定义字段名
    add_data: list[Item] = Field(..., alias="add_data")

@router.post("/batch")
async def batch_add_items(request: ItemListRequest):
    items = request.add_data
    return {"message": f"已接受 {len(items)} 条数据"}

# 请求示例：
# POST /batch
# {
#   "add_data": [
#     {"name": "Item 1", "price": 10.0},
#     {"name": "Item 2", "price": 20.0}
#   ]
# }
```

---

## 5️⃣ 完整实际示例

### 创建 Schema

```python
# src/demo/schemas.py

from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: str | None = Field(None, description="描述")
    price: float = Field(..., ge=0, description="价格")

class BatchItemRequest(BaseModel):
    """批量创建请求"""
    items: list[ItemCreate] = Field(..., description="项目列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"name": "Item 1", "price": 10.0},
                    {"name": "Item 2", "price": 20.0}
                ]
            }
        }
```

### 在路由中使用

```python
# src/demo/router.py

@router.post(
    "/batch",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="批量创建 Item"
)
async def batch_add_items(
    request: BatchItemRequest,  # ← 使用包装体
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """
    批量创建 Item
    
    请求示例：
    {
      "items": [
        {"name": "Item 1", "price": 10.0},
        {"name": "Item 2", "price": 20.0}
      ]
    }
    """
    items = request.items
    
    # 创建后台任务
    asyncio.create_task(create_items_batch_background(items_data=items))
    
    return MessageResponse(
        code=202,
        message="success",
        data=f"已接受 {len(items)} 条数据，正在后台处理..."
    )
```

---

## 6️⃣ 多个请求体参数

### 场景：接收多个不同的对象

```python
class UserData(BaseModel):
    username: str
    email: str

class SettingsData(BaseModel):
    theme: str
    language: str

@router.post("/setup")
async def setup(
    user: UserData,
    settings: SettingsData,
):
    """接收多个请求体参数"""
    return {
        "user": user,
        "settings": settings
    }

# 请求示例：
# POST /setup
# {
#   "user": {"username": "john", "email": "john@example.com"},
#   "settings": {"theme": "dark", "language": "en"}
# }
```

---

## 7️⃣ 混合查询参数和请求体

```python
class Item(BaseModel):
    name: str
    price: float

@router.post("/items")
async def create_item(
    item: Item,  # 请求体
    skip: int = Query(0),  # 查询参数
    limit: int = Query(10),  # 查询参数
):
    """混合使用请求体和查询参数"""
    return {
        "item": item,
        "skip": skip,
        "limit": limit
    }

# 请求示例：
# POST /items?skip=0&limit=10
# {"name": "Apple", "price": 9.99}
```

---

## 8️⃣ 嵌套对象

### 场景：对象包含其他对象

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    email: str
    address: Address

@router.post("/users")
async def create_user(user: User):
    """接收嵌套对象"""
    return user

# 请求示例：
# POST /users
# {
#   "name": "John",
#   "email": "john@example.com",
#   "address": {
#     "street": "Main St 123",
#     "city": "New York",
#     "country": "USA"
#   }
# }
```

---

## 9️⃣ 数组中的嵌套对象

```python
class Item(BaseModel):
    name: str
    tags: list[str]  # 嵌套数组

class Order(BaseModel):
    order_id: str
    items: list[Item]  # Item 对象数组

@router.post("/orders")
async def create_order(order: Order):
    """接收包含嵌套对象数组的请求"""
    return order

# 请求示例：
# POST /orders
# {
#   "order_id": "ORD-001",
#   "items": [
#     {
#       "name": "Item 1",
#       "tags": ["new", "popular"]
#     },
#     {
#       "name": "Item 2",
#       "tags": ["sale"]
#     }
#   ]
# }
```

---

## 🔟 Swagger 文档自动生成

FastAPI 会自动为所有请求体生成 Swagger 文档。访问：

```
http://localhost:8000/docs
```

你会看到：
- 📋 请求体的 JSON Schema
- 📝 示例请求
- ✅ 字段验证规则
- 📖 字段描述

---

## 比较表

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| `items: list[Item]` | 直接数组 | 简单 | 无命名 |
| `ItemListRequest` | 命名对象数组 | 清晰、易维护 | 需要创建 Schema |
| `Body(..., embed=True)` | 动态命名 | 灵活 | 代码复杂 |
| `Field(alias="...")` | 自定义字段名 | 兼容不同格式 | 需要别名配置 |

---

## 最佳实践

### ✅ 推荐做法

```python
# 1. 为每个请求创建明确的 Schema
class BatchItemRequest(BaseModel):
    items: list[ItemCreate]
    
# 2. 在路由中使用
@router.post("/batch")
async def batch_add(request: BatchItemRequest):
    for item in request.items:
        # 处理...
        pass

# 3. 自动生成 Swagger 文档
# 访问 /docs 查看示例
```

### ❌ 避免做法

```python
# 不要：模糊的 dict 类型
@router.post("/batch")
async def batch_add(data: dict):
    # 失去类型提示和验证
    pass

# 不要：不必要的复杂
@router.post("/batch")
async def batch_add(items: list[Item] = Body(..., embed=True, media_type="application/json")):
    # 过度配置
    pass
```

---

## 你的项目中的应用

### 当前代码改进

**之前**（接收直接数组）：
```python
@router.post("/batch")
async def batch_add_items(items_data: list[ItemCreate]):
    # 前端：直接发送数组
    # [{"name": "Item 1", ...}, ...]
    pass
```

**改进后**（接收命名对象）：
```python
# Schema
class BatchItemRequest(BaseModel):
    items: list[ItemCreate]

# 路由
@router.post("/batch")
async def batch_add_items(request: BatchItemRequest):
    items = request.items
    # 前端：发送命名对象
    # {"items": [{"name": "Item 1", ...}, ...]}
    pass
```

---

## 常见问题

### Q: 前端发的是 `{ "add_data": [...] }`，如何接收？

```python
class BatchRequest(BaseModel):
    add_data: list[ItemCreate]

@router.post("/batch")
async def batch_add(request: BatchRequest):
    items = request.add_data
```

### Q: 如何同时接收数组和其他参数？

```python
class BatchRequest(BaseModel):
    items: list[ItemCreate]
    priority: int = 1
    description: str | None = None

@router.post("/batch")
async def batch_add(request: BatchRequest):
    items = request.items
    priority = request.priority
```

### Q: 如何验证每个项目的字段？

```python
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)  # 大于 0

class BatchRequest(BaseModel):
    items: list[ItemCreate]  # 自动验证每个元素

# FastAPI 会自动验证每个 Item
```

---

## 总结

- 📝 使用 **Schema 类** 定义请求体结构
- 📦 使用 **嵌套 Schema** 处理复杂数据
- ✅ FastAPI **自动验证** 请求数据
- 📖 自动生成 **Swagger 文档**
- 🔍 获得完整的 **IDE 类型提示**

