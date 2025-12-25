"""
Demo 模块 - 业务逻辑层
演示如何组织业务逻辑
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import BaseCRUD
from src.common.database import db_manager
from src.demo.models import Item
from src.demo.schemas import ItemCreate, ItemResponse, ItemUpdate
from src.common.exceptions import NotFoundException


class ItemCRUD(BaseCRUD[Item, ItemCreate, ItemUpdate]):
    """Item CRUD 操作类"""
    pass


# CRUD 实例
item_crud = ItemCRUD(Item)


async def get_item_by_id(db: AsyncSession, item_id: int) -> dict[str, Any]:
    """
    根据 ID 获取 Item
    
    Args:
        db: 数据库会话
        item_id: Item ID
    
    Returns:
        Item 数据字典
    
    Raises:
        NotFoundException: 当 Item 不存在时
    """
    item = await item_crud.get(db=db, id=item_id)
    if not item:
        raise NotFoundException(detail=f"Item {item_id} 不存在")
    return item


async def get_items(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    is_active: bool | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """
    获取 Item 列表
    
    Args:
        db: 数据库会话
        offset: 偏移量
        limit: 限制数量
        is_active: 是否激活过滤
        category: 分类过滤
    
    Returns:
        包含 data 和 total_count 的字典
    """
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    if category is not None:
        filters["category"] = category

    return await item_crud.get_multi(
        db=db,
        offset=offset,
        limit=limit,
        **filters,
    )


async def create_item(db: AsyncSession, item_data: ItemCreate) -> dict[str, Any]:
    """
    创建 Item
    
    Args:
        db: 数据库会话
        item_data: 创建数据
    
    Returns:
        创建的 Item 数据字典（包含自增 ID）
    """
    # 使用 create_and_get 创建后立即返回完整的记录（包含自增 ID）
    # 根据唯一字段 name 查询新创建的记录
    return await item_crud.create_and_get(
        db=db,
        object=item_data,
        name=item_data.name,
    )


async def update_item(
    db: AsyncSession,
    item_id: int,
    item_data: ItemUpdate,
) -> dict[str, Any]:
    """
    更新 Item
    
    Args:
        db: 数据库会话
        item_id: Item ID
        item_data: 更新数据
    
    Returns:
        更新后的 Item 数据
    
    Raises:
        NotFoundException: 当 Item 不存在时
    """
    # 先检查是否存在
    await get_item_by_id(db, item_id)

    # 过滤掉 None 值
    update_data = item_data.model_dump(exclude_unset=True)
    if update_data:
        await item_crud.update(db=db, object=update_data, id=item_id)

    return await get_item_by_id(db, item_id)


async def delete_item(db: AsyncSession, item_id: int) -> None:
    """
    删除 Item
    
    Args:
        db: 数据库会话
        item_id: Item ID
    
    Raises:
        NotFoundException: 当 Item 不存在时
    """
    # 先检查是否存在
    await get_item_by_id(db, item_id)
    await item_crud.delete(db=db, id=item_id)


async def create_items_batch(
    db: AsyncSession,
    items_data: list[ItemCreate],
) -> list[dict[str, Any]]:
    """
    批量创建 Item（优化版，毫秒级性能）
    
    Args:
        db: 数据库会话
        items_data: 要创建的 Item 列表
    
    Returns:
        创建的 Item 列表（包含 ID 和时间戳）
    """
    # 使用批量创建方法，一次性插入所有数据
    
    return await item_crud.create_many(db=db, objects=items_data)


async def create_items_batch_background(
    items_data: list[ItemCreate],
) -> None:
    """
    后台批量创建 Item（独立数据库会话）
    
    这个函数用于后台任务，创建独立的数据库会话
    避免与主请求的会话冲突
    
    Args:
        items_data: 要创建的 Item 列表
    """
    # 创建独立的数据库会话，用于后台任务
    session_factory = db_manager.get_session_factory()
    async with session_factory() as session:
        try:
            await item_crud.create_many(db=session, objects=items_data)
            await session.commit()
            print(f"[后台任务] 成功创建 {len(items_data)} 条记录")
        except Exception as e:
            await session.rollback()
            print(f"[后台任务] 创建失败: {e}")
        finally:
            await session.close()

