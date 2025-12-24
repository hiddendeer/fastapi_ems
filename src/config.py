"""
全局配置管理
使用 Pydantic BaseSettings 进行类型安全的配置管理
"""
from functools import lru_cache
from typing import Any

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Settings(BaseSettings):
    """应用全局配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    APP_NAME: str = "FastAPI EMS"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于 FastAPI 的企业管理系统框架"
    DEBUG: bool = False
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # CORS 配置
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # 数据库配置 - 主数据库
    # 从 .env 文件读取，没有则使用空字符串（必须通过环境变量配置）
    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""  # 默认数据库
    DB_ECHO: bool = False  # 是否打印 SQL 语句

    # 多数据库配置
    DB_USER_NAME: str = "myems_user_db"
    DB_SYSTEM_NAME: str = "myems_system_db"
    DB_REPORTING_NAME: str = "myems_reporting_db"

    # 连接池配置
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800  # 改为 30 分钟（防止长时间空闲断连）

    @property
    def DATABASE_URL(self) -> str:
        """主数据库连接 URL"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """主数据库同步连接 URL (用于 Alembic 迁移)"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    def get_database_url(self, db_name: str) -> str:
        """获取指定数据库的连接 URL"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{db_name}?charset=utf8mb4"

    @property
    def SHOW_DOCS(self) -> bool:
        """是否显示 API 文档"""
        return self.ENVIRONMENT in (Environment.DEVELOPMENT, Environment.STAGING)

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        """验证配置"""
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if self.DEBUG:
                raise ValueError("生产环境不允许开启 DEBUG 模式")
        return self


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()

