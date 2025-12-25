"""
分页工具模块
"""
import math
from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel

from src.common.schemas import PageInfo


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 10

    @property
    def offset(self) -> int:
        """计算偏移量，用于数据库查询"""
        return (self.page - 1) * self.page_size


def get_pagination(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
) -> PaginationParams:
    """
    分页参数依赖
    
    使用示例:
        @router.get("/items")
        async def get_items(pagination: PaginationParams = Depends(get_pagination)):
            result = await service.get_items(
                offset=pagination.offset,  # 直接使用 offset 属性
                limit=pagination.page_size
            )
            ...
    """
    return PaginationParams(page=page, page_size=page_size)


def calculate_page_info(total: int, page: int, page_size: int) -> PageInfo:
    """
    计算分页信息
    
    Args:
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
    
    Returns:
        PageInfo: 分页信息对象
    """
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    return PageInfo(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def get_offset(page: int, page_size: int) -> int:
    """计算偏移量"""
    return (page - 1) * page_size

