"""
Demo 模块 - 依赖项
演示如何定义和使用依赖项
"""
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db
from src.demo import service


async def valid_item_id(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    验证 Item ID 是否存在
    
    这是一个依赖项，可以在多个路由中复用
    如果 Item 不存在，会自动抛出 404 异常
    
    使用示例:
        @router.get("/items/{item_id}")
        async def get_item(item: dict = Depends(valid_item_id)):
            return item
    """
    return await service.get_item_by_id(db, item_id)


    

