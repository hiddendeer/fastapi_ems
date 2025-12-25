"""
全局常量定义
"""
from enum import Enum


class Environment(str, Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class OrderDirection(str, Enum):
    """排序方向"""
    ASC = "asc"
    DESC = "desc"

