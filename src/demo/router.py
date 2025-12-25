"""
Demo 模块 - 路由定义
演示 RESTful API 的标准实现
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db
from src.demo.dependencies import valid_item_id
from src.demo.service import (
    create_item as create_item_service,
    create_items_batch,
    create_items_batch_background,
    delete_item as delete_item_service,
    get_item_by_id,
    get_items,
    update_item as update_item_service,
)
from src.demo.schemas import (
    BatchItemRequest,
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemUpdate,
)
from src.common.pagination import PaginationParams, get_pagination
from src.common.schemas import MessageResponse


router = APIRouter(prefix="/items", tags=["Demo - Items"])


@router.get(
    "",
    response_model=ItemListResponse,
    summary="获取 Item 列表",
    description="获取 Item 列表，支持分页和过滤",
)
async def list_items(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    is_active: bool | None = Query(None, description="是否激活"),
    category: str | None = Query(None, description="分类"),
) -> ItemListResponse:
    """获取 Item 列表"""
    result = await get_items(
        db=db,
        offset=pagination.offset,
        limit=pagination.page_size,
        is_active=is_active,
        category=category,
    )
    
    # Pydantic 会自动将 datetime 对象序列化为字符串
    items_list = [ItemResponse(**item) for item in result.get("data", [])]
    
    return ItemListResponse(
        data=items_list,
        total=result.get("total_count", 0),
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="获取单个 Item",
    description="根据 ID 获取单个 Item",
)
async def get_item(
    item: dict[str, Any] = Depends(valid_item_id),
) -> ItemResponse:
    """获取单个 Item"""
    return ItemResponse(**item)


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建 Item",
    description="创建新的 Item",
)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """创建 Item"""
    item = await create_item_service(db=db, item_data=item_data)
    # create_item_service 返回的已经是字典，包含自增 ID
    return ItemResponse(**item)


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="更新 Item",
    description="更新指定 ID 的 Item",
)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """更新 Item"""
    item = await update_item_service(db=db, item_id=item_id, item_data=item_data)
    return ItemResponse(**item)


@router.delete(
    "/{item_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="删除 Item",
    description="删除指定 ID 的 Item",
)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """删除 Item"""
    await delete_item_service(db=db, item_id=item_id)
    return MessageResponse(
        code=200,
        message="success",
        data=f"Item {item_id} 已删除"
    )

@router.post(
    "/batch",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="批量创建 Item",
    description="批量创建多个 Item（后台异步，毫秒级响应）",
)
async def batch_add_items(
    request: BatchItemRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    items_data = request.items
    
    # 创建后台任务，使用独立的数据库会话，不等待结果
    asyncio.create_task(create_items_batch_background(items_data=items_data))
    
    # 立即返回成功消息
    return MessageResponse(
        code=202,
        message="success",
        data=f"已接受 {len(items_data)} 条数据，正在后台处理..."
    )





