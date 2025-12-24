# User 对象属性和使用方法完全指南

## 目录
- [1. User 对象概览](#1-user-对象概览)
- [2. 属性分类详解](#2-属性分类详解)
- [3. 常见使用方法](#3-常见使用方法)
- [4. 实际代码示例](#4-实际代码示例)
- [5. 数据转换方法](#5-数据转换方法)
- [6. 常见问题](#6-常见问题)

---

## 1. User 对象概览

`User` 是一个 SQLAlchemy ORM 对象，从数据库查询返回。它继承自 `BaseModel`，包含以下几类属性：

### 属性总表

| 属性名 | 数据类型 | 是否必需 | 说明 |
|--------|---------|--------|------|
| **主键和唯一标识** |
| `id` | `int` | ✅ | 用户主键 ID（自动递增） |
| `openid` | `str` | ✅ | 微信 openid（唯一） |
| `unionid` | `str \| None` | ❌ | 微信 unionid（唯一） |
| **个人信息** |
| `nickname` | `str \| None` | ❌ | 用户昵称 |
| `avatar_url` | `str \| None` | ❌ | 用户头像 URL |
| `gender` | `int` | ⚠️ | 性别：0-未知，1-男，2-女 |
| **地址信息** |
| `country` | `str \| None` | ❌ | 国家 |
| `province` | `str \| None` | ❌ | 省份 |
| `city` | `str \| None` | ❌ | 城市 |
| `language` | `str` | ⚠️ | 语言（默认 zh_CN） |
| **联系方式** |
| `phone_number` | `str \| None` | ❌ | 手机号（唯一） |
| `country_code` | `str` | ⚠️ | 国家区号（默认 +86） |
| **账户状态** |
| `is_active` | `bool` | ⚠️ | 是否激活（默认 True） |
| `is_verified` | `bool` | ⚠️ | 是否实名认证（默认 False） |
| `user_type` | `int` | ⚠️ | 用户类型：1-普通，2-VIP，9-管理员 |
| `status` | `int` | ⚠️ | 账号状态：0-禁用，1-正常，2-冻结 |
| **注册和登录信息** |
| `register_source` | `str` | ⚠️ | 注册来源（默认 miniprogram） |
| `session_key` | `str \| None` | ❌ | 微信 session_key |
| `first_login_time` | `datetime \| None` | ❌ | 首次登录时间 |
| `last_login_time` | `datetime \| None` | ❌ | 最后登录时间 |
| `login_count` | `int` | ⚠️ | 登录次数（默认 0） |
| `last_login_ip` | `str \| None` | ❌ | 最后登录 IP |
| **扩展信息** |
| `extra_info` | `dict \| None` | ❌ | 扩展信息（JSON 格式） |
| **时间戳** |
| `created_at` | `datetime` | ✅ | 创建时间（继承自 BaseModel） |
| `updated_at` | `datetime` | ✅ | 更新时间（继承自 BaseModel） |
| `deleted_at` | `datetime \| None` | ❌ | 软删除时间 |

---

## 2. 属性分类详解

### 2.1 基本身份信息（必需）

```python
user = result_id  # User 对象

# 用户的唯一标识
print(user.id)          # int，主键 ID，自动递增
print(user.openid)      # str，微信 openid（微信生态中的唯一标识）
print(user.unionid)     # str | None，微信 unionid（跨小程序唯一标识）
```

**用法：**
```python
# 检查用户是否存在
if user is None:
    print("用户不存在")
else:
    print(f"用户 ID: {user.id}")

# 使用 openid 作为唯一标识查询
if user.openid == "某个openid":
    print("这是特定微信用户")
```

### 2.2 个人信息

```python
# 获取用户个人信息
nickname = user.nickname           # str | None，用户昵称
avatar_url = user.avatar_url       # str | None，用户头像 URL
gender = user.gender               # int，性别（0=未知，1=男，2=女）

# 性别映射
gender_map = {0: "未知", 1: "男", 2: "女"}
gender_text = gender_map.get(user.gender, "未知")
print(f"用户昵称：{nickname}，性别：{gender_text}")
```

**用法：**
```python
# 显示用户资料
if user.nickname:
    print(f"昵称：{user.nickname}")
else:
    print("用户未设置昵称")

# 下载用户头像
if user.avatar_url:
    download_image(user.avatar_url)
```

### 2.3 地址信息

```python
# 获取用户地址信息
country = user.country              # str | None，国家
province = user.province            # str | None，省份
city = user.city                    # str | None，城市
language = user.language            # str，语言代码（如 zh_CN, en_US）

# 组合地址
full_address = f"{country or ''} {province or ''} {city or ''}".strip()
print(f"用户地址：{full_address}")
print(f"语言：{language}")
```

**用法：**
```python
# 检查用户是否完整填写地址
has_complete_address = all([user.country, user.province, user.city])
if has_complete_address:
    print("地址完整")
else:
    print("地址信息不完整")

# 根据语言提供本地化内容
if user.language == "en_US":
    send_message_in_english(user)
elif user.language == "zh_CN":
    send_message_in_chinese(user)
```

### 2.4 联系方式

```python
# 获取联系方式
phone_number = user.phone_number    # str | None，手机号
country_code = user.country_code    # str，国家区号（如 +86）

# 完整电话号码
if phone_number:
    full_phone = f"{country_code}{phone_number}"
    print(f"电话号码：{full_phone}")
```

**用法：**
```python
# 检查是否绑定手机
if user.phone_number:
    print(f"已绑定手机：{user.country_code}{user.phone_number}")
else:
    print("未绑定手机")

# 发送短信验证码
if user.phone_number:
    send_sms(user.country_code + user.phone_number, code)
```

### 2.5 账户状态

```python
# 获取账户状态
is_active = user.is_active          # bool，是否激活
is_verified = user.is_verified      # bool，是否实名认证
user_type = user.user_type          # int，用户类型
status = user.status                # int，账号状态

# 用户类型映射
user_type_map = {1: "普通用户", 2: "VIP用户", 9: "管理员"}
print(f"用户类型：{user_type_map.get(user_type, '未知')}")

# 账号状态映射
status_map = {0: "禁用", 1: "正常", 2: "冻结"}
print(f"账号状态：{status_map.get(status, '未知')}")
```

**用法：**
```python
# 权限检查
if not user.is_active:
    raise PermissionError("用户账号已禁用")

if user.status != 1:
    raise PermissionError("用户账号异常")

if user.is_verified:
    print("用户已实名认证")

# VIP 功能访问控制
if user.user_type == 2:
    enable_vip_features()
elif user.user_type == 9:
    enable_admin_features()
else:
    enable_basic_features()
```

### 2.6 注册和登录信息

```python
# 获取注册登录信息
register_source = user.register_source      # str，注册来源
session_key = user.session_key              # str | None，微信 session_key
first_login_time = user.first_login_time   # datetime | None，首次登录
last_login_time = user.last_login_time     # datetime | None，最后登录
login_count = user.login_count              # int，登录次数
last_login_ip = user.last_login_ip         # str | None，最后登录 IP

# 计算用户活跃度
days_since_last_login = (datetime.now() - user.last_login_time).days if user.last_login_time else None
print(f"用户已登录 {user.login_count} 次")
print(f"距上次登录已 {days_since_last_login} 天")
```

**用法：**
```python
# 统计新用户
if (datetime.now() - user.created_at).days < 7:
    print("新注册用户")

# 识别沉睡用户
if user.last_login_time and (datetime.now() - user.last_login_time).days > 30:
    send_reactivation_email(user)

# 获取用户来源统计
register_sources = {
    "miniprogram": "小程序",
    "web": "网页",
    "app": "App"
}
source = register_sources.get(user.register_source, "未知")
print(f"用户来源：{source}")
```

### 2.7 扩展信息（JSON）

```python
# 获取扩展信息
extra_info = user.extra_info        # dict | None，JSON 格式的扩展数据

# 访问 JSON 字段中的数据
if extra_info:
    custom_field = extra_info.get("field_name")
    print(f"自定义字段：{custom_field}")
```

**用法：**
```python
# 存储额外的用户信息
extra_info = {
    "preferences": {
        "theme": "dark",
        "notification": True
    },
    "custom_attributes": {
        "vip_level": 3,
        "invite_code": "ABC123"
    }
}
# 保存到数据库时
user.extra_info = extra_info
await db.commit()

# 之后查询时
if user.extra_info and "vip_level" in user.extra_info["custom_attributes"]:
    vip_level = user.extra_info["custom_attributes"]["vip_level"]
    print(f"VIP 等级：{vip_level}")
```

### 2.8 时间戳字段

```python
# 获取时间戳
created_at = user.created_at        # datetime，创建时间
updated_at = user.updated_at        # datetime，最后更新时间
deleted_at = user.deleted_at        # datetime | None，软删除时间

# 计算账号年龄
account_age_days = (datetime.now() - user.created_at).days
print(f"账号已创建 {account_age_days} 天")

# 检查是否被软删除
if user.deleted_at:
    print("该用户已被删除")
else:
    print("用户账号正常")
```

---

## 3. 常见使用方法

### 3.1 直接属性访问（点操作符）

```python
# 这是最常见的方式
user = result_id  # User 对象

# 直接访问属性
print(user.id)              # 输出：1
print(user.nickname)        # 输出：张三
print(user.is_active)       # 输出：True
print(user.created_at)      # 输出：2024-01-01 12:00:00
```

### 3.2 安全访问（使用 getattr）

```python
# 当不确定属性是否存在时
nickname = getattr(user, 'nickname', '未知')
avatar = getattr(user, 'avatar_url', 'default.jpg')
```

### 3.3 批量属性访问

```python
# 获取所有属性字典
from sqlalchemy.orm import object_as_dict
user_dict = object_as_dict(user)
print(user_dict)

# 或使用 __dict__
for key, value in user.__dict__.items():
    if not key.startswith('_'):  # 跳过私有属性
        print(f"{key}: {value}")
```

### 3.4 条件判断

```python
# 检查用户状态
if user and user.is_active and user.status == 1:
    print("用户可用")

# 检查必需信息
if user.nickname and user.avatar_url:
    print("用户信息完整")

# 检查认证状态
if not user.is_verified:
    print("用户未实名认证，需要完成认证")
```

---

## 4. 实际代码示例

### 4.1 在 router 中的用法（当前代码）

```python
from src.projectApi.service import get_user_id
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/info")
async def get_project_info(
    just_id: str = Query(None, description="JustID"),
    db: AsyncSession = Depends(get_db),
) -> ResponseModel:
    """获取项目列表"""
    
    # 获取 User 对象
    result_id = await get_user_id(db=db, user_id=just_id)
    
    # 检查用户是否存在
    if result_id is None:
        return ResponseModel(
            code=404,
            message="用户不存在",
            data=None
        )
    
    # 获取用户昵称（第 28 行的用法）
    nickname = result_id.nickname
    print(nickname, "nickname")
    
    # 获取其他属性
    user_id = result_id.id
    openid = result_id.openid
    is_active = result_id.is_active
    
    # 返回响应
    return ResponseModel(
        code=200,
        message="success",
        data={
            "id": user_id,
            "nickname": nickname,
            "openid": openid,
            "is_active": is_active
        }
    )
```

### 4.2 完整的用户信息展示

```python
async def get_user_profile(user_id: int, db: AsyncSession):
    """获取完整的用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # 构建完整用户信息
    profile = {
        # 基本信息
        "id": user.id,
        "openid": user.openid,
        "unionid": user.unionid,
        
        # 个人信息
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "gender": {0: "未知", 1: "男", 2: "女"}.get(user.gender, "未知"),
        
        # 地址
        "location": {
            "country": user.country,
            "province": user.province,
            "city": user.city,
            "language": user.language
        },
        
        # 账户状态
        "account": {
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "status": {0: "禁用", 1: "正常", 2: "冻结"}.get(user.status, "未知"),
            "user_type": {1: "普通用户", 2: "VIP用户", 9: "管理员"}.get(user.user_type, "未知")
        },
        
        # 登录信息
        "login": {
            "first_login_time": user.first_login_time.isoformat() if user.first_login_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
            "login_count": user.login_count,
            "last_login_ip": user.last_login_ip
        },
        
        # 时间戳
        "timestamps": {
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None
        }
    }
    
    return profile
```

### 4.3 用户权限检查

```python
async def check_user_permission(user_id: int, db: AsyncSession, required_type: int = None):
    """检查用户权限"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    # 用户不存在
    if not user:
        raise NotFoundException("用户不存在")
    
    # 用户已禁用
    if not user.is_active:
        raise PermissionError("用户账户已禁用")
    
    # 用户账号异常
    if user.status != 1:
        raise PermissionError(f"用户账号状态异常：{user.status}")
    
    # 检查用户类型权限
    if required_type and user.user_type != required_type:
        raise PermissionError(f"权限不足，需要 {required_type} 级别")
    
    return user

# 使用示例
try:
    user = await check_user_permission(user_id=1, db=db, required_type=9)  # 需要管理员权限
    # 执行操作
except PermissionError as e:
    return ResponseModel(code=403, message=str(e))
```

---

## 5. 数据转换方法

### 5.1 转换为字典

```python
# 方法 1：使用 SQLAlchemy 的 object_as_dict
from sqlalchemy.orm import object_as_dict

user_dict = object_as_dict(user)
print(user_dict)  # {'id': 1, 'openid': '...', 'nickname': '...', ...}

# 方法 2：手动构建
user_dict = {
    'id': user.id,
    'openid': user.openid,
    'nickname': user.nickname,
    'is_active': user.is_active,
    'created_at': user.created_at.isoformat(),
}

# 方法 3：排除某些字段
exclude_fields = {'session_key', 'deleted_at'}
user_dict = {k: v for k, v in object_as_dict(user).items() if k not in exclude_fields}
```

### 5.2 转换为 Pydantic Schema

```python
from pydantic import BaseModel
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    openid: str
    nickname: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # SQLAlchemy 兼容性

# 转换
user_response = UserResponse.from_orm(user)
# 或直接使用构造器
user_response = UserResponse(**object_as_dict(user))
```

### 5.3 转换为 JSON

```python
import json
from datetime import datetime

# 自定义 JSON 编码器处理 datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

user_dict = object_as_dict(user)
user_json = json.dumps(user_dict, cls=DateTimeEncoder)
print(user_json)
```

---

## 6. 常见问题

### Q1: User 对象为 None 时如何处理？

```python
result_id = await get_user_id(db=db, user_id=just_id)

# ✅ 正确做法
if result_id is None:
    return ResponseModel(code=404, message="用户不存在")

# 获取昵称时也要检查
nickname = result_id.nickname if result_id else None

# 或使用链式安全访问
nickname = result_id.nickname if result_id else "未知"
```

### Q2: 如何修改 User 对象的属性并保存？

```python
# 修改属性
user.nickname = "新昵称"
user.is_active = False
user.last_login_time = datetime.now()

# 提交到数据库
await db.commit()

# 刷新对象以获取数据库生成的值
await db.refresh(user)
```

### Q3: 如何检查属性是否为 None？

```python
# 检查可空属性
if user.nickname is not None:
    print(f"昵称：{user.nickname}")

# 或使用更安全的方式
nickname = user.nickname or "未设置昵称"

# 检查多个属性
if all([user.nickname, user.avatar_url]):
    print("信息完整")
```

### Q4: User 对象和字典有什么区别？

```python
# User 对象
user = result.scalar_one_or_none()
print(user.nickname)  # 属性访问
print(type(user))     # <class 'src.projectApi.models.User'>

# 字典
user_dict = object_as_dict(user)
print(user_dict['nickname'])  # 键访问
print(type(user_dict))  # <class 'dict'>

# 对象可以直接关联其他 ORM 对象，字典不行
# user.posts（如果有关系）
# user_dict.posts  ❌ 错误
```

### Q5: 如何避免 "对象已过期" 错误？

```python
# ❌ 错误：会话关闭后访问对象属性会报错
async def bad_example(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user  # 会话关闭后再访问会出错

# ✅ 正确：确保在会话内访问，或使用 expire_on_commit=False
async def good_example(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    # 在会话关闭前访问所有属性
    data = {
        'id': user.id,
        'nickname': user.nickname,
        'created_at': user.created_at
    }
    return data
```

---

## 总结

**User 对象是 SQLAlchemy 的 ORM 模型实例，可以：**

1. ✅ 直接访问属性：`user.nickname`
2. ✅ 检查状态：`if user.is_active`
3. ✅ 计算值：`user.login_count + 1`
4. ✅ 修改并保存：`user.nickname = "new"`
5. ✅ 转换为字典/JSON：`object_as_dict(user)`
6. ✅ 转换为 Pydantic Schema：`UserResponse.from_orm(user)`

**重点记住：** User 对象有 40+ 个属性，都可以通过点操作符直接访问！

