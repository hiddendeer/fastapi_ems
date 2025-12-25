"""
Demo 模块 - 数据库模型
演示如何定义 SQLAlchemy 模型
"""
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.common.models import BaseModel


class Item(BaseModel):
    """
    示例项目模型
    演示一个典型的数据库模型定义
    """
    __tablename__ = "demo_item"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="项目名称",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="项目描述",
    )
    price: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="价格",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否激活",
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="分类",
    )

