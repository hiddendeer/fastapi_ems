"""
用户模块 - 业务逻辑层
演示如何组织业务逻辑
"""
from typing import Any
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import BaseCRUD
from src.projectApi.models import User
from src.demo.models import Item
from src.projectApi.schemas import UserCreate, UserResponse, UserUpdate
from src.common.exceptions import NotFoundException


class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
    """用户 CRUD 操作类"""
    pass


# CRUD 实例
user_crud = UserCRUD(User)


# 业务逻辑函数

async def get_user_by_id(db: AsyncSession, user_id: int) -> dict[str, Any]:
    """
    根据 ID 获取用户
    """
    user = await user_crud.get(db=db, id=user_id)
    if not user:
        raise NotFoundException(detail=f"用户 {user_id} 不存在")
    return user


async def get_user_by_openid(db: AsyncSession, openid: str) -> dict[str, Any] | None:
    """
    根据微信 openid 获取用户
    """
    return await user_crud.get(db=db, openid=openid)

async def get_user_id(db: AsyncSession, user_id: int) -> dict[str, Any] | None:
    """
    根据用户ID获取用户及其关联的Item，返回字典或 None
    """
    result = await db.execute(
        select(User.nickname, Item.name).outerjoin(
            User, User.id == Item.id
        ).where(
            User.id == user_id
        )
    )
    
    result_handle = result.all()
    
    # 如果没有查询到数据，返回 None
    if not result_handle:
        return None
    
    # 提取第一条记录的用户昵称（所有记录的用户昵称相同）
    user_nickname = result_handle[0].nickname
    
    # 构建返回字典
    return {
        "nickname": user_nickname,
        "items": [
            {"item_name": row.name}
            for row in result_handle
        ],
        "item_count": len(result_handle)
    }

async def get_users(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    status: int | None = None,
    is_active: bool | None = None,
    user_type: int | None = None,
) -> dict[str, Any]:
    """
    获取用户列表
    """
    filters = {}
    if status is not None:
        filters["status"] = status
    if is_active is not None:
        filters["is_active"] = is_active
    if user_type is not None:
        filters["user_type"] = user_type

    result = await user_crud.get_multi(
        db=db,
        offset=offset,
        limit=limit,
        **filters,
    )

    
    return result


async def create_user(db: AsyncSession, user_data: UserCreate) -> dict[str, Any]:
    """
    创建用户
    """
    return await user_crud.create_and_get(
        db=db,
        object=user_data,
        openid=user_data.openid,
    )


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdate,
) -> dict[str, Any]:
    """
    更新用户信息
    """
    # 先检查是否存在
    await get_user_by_id(db, user_id)

    # 过滤掉 None 值
    update_data = user_data.model_dump(exclude_unset=True)
    if update_data:
        await user_crud.update(db=db, object=update_data, id=user_id)

    return await get_user_by_id(db, user_id)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    """
    删除用户（软删除）
    """
    # 先检查是否存在
    await get_user_by_id(db, user_id)
    
    # 软删除：设置 deleted_at
    await user_crud.update(
        db=db,
        object={"deleted_at": datetime.now()},
        id=user_id
    )


async def update_login_info(
    db: AsyncSession,
    user_id: int,
    login_ip: str | None = None,
) -> None:
    """
    更新用户登录信息
    """
    update_data = {
        "last_login_time": datetime.now(),
    }
    if login_ip:
        update_data["last_login_ip"] = login_ip
    
    # 如果是首次登录，设置 first_login_time
    user = await get_user_by_id(db, user_id)
    if user.get("first_login_time") is None:
        update_data["first_login_time"] = datetime.now()
    
    # 增加登录次数
    update_data["login_count"] = (user.get("login_count") or 0) + 1
    
    await user_crud.update(db=db, object=update_data, id=user_id)