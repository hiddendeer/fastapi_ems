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

    # ========== 应用配置 ==========
    # 来自 .env 文件或环境变量
    APP_NAME: str = "FastAPI EMS"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于 FastAPI 的企业管理系统框架"
    DEBUG: bool = False
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # ========== API 配置 ==========
    # 来自 .env 文件或环境变量
    API_V1_PREFIX: str = "/api/v1"

    # ========== 服务器配置 ==========
    # 来自 .env 文件或环境变量
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ========== CORS 配置 ==========
    # 来自 .env 文件或环境变量
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ========== 数据库配置 - 主数据库 ==========
    # 重要：这些字段必须在 .env 文件中配置
    # 对应 .env 中的字段：DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_ECHO
    DB_HOST: str = ""  # .env: DB_HOST
    DB_PORT: int = 3306  # .env: DB_PORT (默认 MySQL 端口)
    DB_USER: str = ""  # .env: DB_USER
    DB_PASSWORD: str = ""  # .env: DB_PASSWORD
    DB_NAME: str = ""  # .env: DB_NAME (默认数据库)
    DB_ECHO: bool = False  # .env: DB_ECHO (是否打印 SQL 语句)

    # ========== 多数据库配置 ==========
    # 来自 .env 文件或环境变量
    # 对应 .env 中的字段：DB_USER_NAME, DB_SYSTEM_NAME, DB_REPORTING_NAME
    DB_USER_NAME: str = "myems_user_db"  # .env: DB_USER_NAME
    DB_SYSTEM_NAME: str = "myems_system_db"  # .env: DB_SYSTEM_NAME
    DB_REPORTING_NAME: str = "myems_reporting_db"  # .env: DB_REPORTING_NAME

    # ========== 数据库连接池配置 ==========
    # 来自 .env 文件或环境变量
    # 对应 .env 中的字段：DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE
    DB_POOL_SIZE: int = 10  # .env: DB_POOL_SIZE (连接池大小)
    DB_MAX_OVERFLOW: int = 20  # .env: DB_MAX_OVERFLOW (最大溢出连接数)
    DB_POOL_RECYCLE: int = 1800  # .env: DB_POOL_RECYCLE (连接回收时间，秒)

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
        """
        验证配置的有效性
        
        检查项：
        1. 生产环境不允许开启 DEBUG 模式
        2. 必需的数据库配置不能为空
        
        抛出异常：
        - ValueError: 配置验证失败
        """
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if self.DEBUG:
                raise ValueError("生产环境不允许开启 DEBUG 模式")
            
            # 生产环境下检查必需的数据库配置
            if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
                raise ValueError(
                    "生产环境必须配置完整的数据库信息: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
                )
        
        return self
    
    def get_config_summary(self) -> dict[str, Any]:
        """
        获取配置摘要（安全版本，隐藏敏感信息）
        
        返回：
            包含非敏感配置信息的字典
        """
        return {
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
            "debug": self.DEBUG,
            "environment": self.ENVIRONMENT.value,
            "database_host": "***" if self.DB_HOST else "未配置",
            "database_name": "***" if self.DB_NAME else "未配置",
            "api_prefix": self.API_V1_PREFIX,
            "server_host": self.HOST,
            "server_port": self.PORT,
        }


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()

