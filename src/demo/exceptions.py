"""
Demo 模块 - 异常定义
演示如何定义模块特定的异常
"""
from src.common.exceptions import NotFoundException, BadRequestException


class ItemNotFound(NotFoundException):
    """Item 不存在异常"""

    def __init__(self, item_id: int):
        super().__init__(detail=f"Item {item_id} 不存在")


class ItemAlreadyExists(BadRequestException):
    """Item 已存在异常"""

    def __init__(self, name: str):
        super().__init__(detail=f"Item '{name}' 已存在")

