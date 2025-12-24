"""
全局 Pydantic 模型（Schema）
提供通用的请求/响应模型
"""
from datetime import datetime
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, field_serializer


class CustomModel(BaseModel):
    """
    自定义基础模型
    - 统一日期时间格式
    - 提供序列化方法
    """
    model_config = ConfigDict(
        from_attributes=True,  # 支持从 ORM 模型创建
        populate_by_name=True,
    )

    @field_serializer("*", mode="wrap")
    def serialize_datetime(self, value: Any, serializer, info):
        """统一序列化 datetime 字段为易读的标准格式"""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return serializer(value)

    def serializable_dict(self, **kwargs) -> dict[str, Any]:
        """返回可序列化的字典"""
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)


# 泛型类型变量
T = TypeVar("T")


class ResponseModel(CustomModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: T | None = None


class PageInfo(CustomModel):
    """分页信息"""
    page: int = 1
    page_size: int = 10
    total: int = 0
    total_pages: int = 0


class PageResponse(CustomModel, Generic[T]):
    """分页响应模型"""
    code: int = 200
    message: str = "success"
    data: list[T] = []
    page_info: PageInfo


class IdResponse(CustomModel):
    """ID 响应模型"""
    id: int


class MessageResponse(CustomModel, Generic[T]):
    """
    消息响应模型（标准统一格式）
    
    使用示例:
        return MessageResponse(
            code=200,
            message="操作成功",
            data={"id": 1, "name": "Item"}
        )
    """
    code: int = 200
    message: str = "success"
    data: T | None = None


class ErrorResponse(CustomModel):
    """
    错误响应模型（统一的验证/业务错误格式）
    
    使用示例:
        return ErrorResponse(
            code=400,
            message="error",
            errorMessage="项目ID必须大于等于10"
        )
    """
    code: int = 400
    message: str = "error"
    errorMessage: str = "请求处理失败"

