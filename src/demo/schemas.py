"""
Demo 模块 - Pydantic 模型（Schema）
演示请求和响应模型的定义
"""
from datetime import datetime

from pydantic import Field

from src.common.schemas import CustomModel


class ItemBase(CustomModel):
    """Item 基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: str | None = Field(None, description="项目描述")
    price: float = Field(0.0, ge=0, description="价格")
    is_active: bool = Field(True, description="是否激活")
    category: str | None = Field(None, max_length=50, description="分类")


class ItemCreate(ItemBase):
    """创建 Item 请求模型"""
    pass


class ItemUpdate(CustomModel):
    """更新 Item 请求模型（所有字段可选）"""
    name: str | None = Field(None, min_length=1, max_length=100, description="项目名称")
    description: str | None = Field(None, description="项目描述")
    price: float | None = Field(None, ge=0, description="价格")
    is_active: bool | None = Field(None, description="是否激活")
    category: str | None = Field(None, max_length=50, description="分类")


class ItemResponse(ItemBase):
    """Item 响应模型"""
    id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ItemListResponse(CustomModel):
    """Item 列表响应模型"""
    data: list[ItemResponse] = Field(default_factory=list, description="项目列表")
    total: int = Field(0, description="总数")


class BatchItemRequest(CustomModel):
    """
    批量创建 Item 请求模型
    
    使用示例:
        {
          "items": [
            {"name": "Item 1", "price": 10.0},
            {"name": "Item 2", "price": 20.0}
          ]
        }
    """
    items: list[ItemCreate] = Field(..., description="项目列表")

