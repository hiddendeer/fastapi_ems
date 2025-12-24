"""
Demo 模块 - 常量定义
演示如何定义模块特定的常量
"""
from enum import Enum


class ItemCategory(str, Enum):
    """Item 分类枚举"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    OTHER = "other"


# 默认分页大小
DEFAULT_PAGE_SIZE = 10

# 最大分页大小
MAX_PAGE_SIZE = 100

