"""
用户模块 - 数据库模型
微信小程序用户表
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Integer, String, DateTime, Text, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseModel


class User(BaseModel):
    """
    微信小程序用户模型
    存储微信用户的基本信息和登录日志
    """
    __tablename__ = "users"

    # 基本信息
    openid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="微信openid，唯一标识")
    unionid: Mapped[str | None] = mapped_column(String(64), unique=True, default=None, comment="微信unionid")
    session_key: Mapped[str | None] = mapped_column(String(64), default=None, comment="微信session_key")
    
    # 个人信息
    nickname: Mapped[str | None] = mapped_column(String(100), default=None, comment="用户昵称")
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None, comment="用户头像URL")
    gender: Mapped[int] = mapped_column(Integer, default=0, comment="性别：0-未知，1-男，2-女")
    
    # 地址信息
    country: Mapped[str | None] = mapped_column(String(50), default=None, comment="国家")
    province: Mapped[str | None] = mapped_column(String(50), default=None, comment="省份")
    city: Mapped[str | None] = mapped_column(String(50), default=None, comment="城市")
    language: Mapped[str] = mapped_column(String(20), default="zh_CN", comment="语言")
    
    # 联系方式
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, default=None, comment="手机号")
    country_code: Mapped[str] = mapped_column(String(10), default="+86", comment="国家区号")
    
    # 账户状态
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    is_verified: Mapped[bool] = mapped_column(default=False, comment="是否实名认证")
    user_type: Mapped[int] = mapped_column(Integer, default=1, comment="用户类型：1-普通用户，2-VIP用户，9-管理员")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="账号状态：0-禁用，1-正常，2-冻结")
    
    # 注册和登录信息
    register_source: Mapped[str] = mapped_column(String(20), default="miniprogram", comment="注册来源")
    first_login_time: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="首次登录时间")
    last_login_time: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="最后登录时间")
    login_count: Mapped[int] = mapped_column(Integer, default=0, comment="登录次数")
    last_login_ip: Mapped[str | None] = mapped_column(String(50), default=None, comment="最后登录IP")
    
    # 扩展信息
    extra_info: Mapped[dict | None] = mapped_column(JSON, default=None, comment="扩展信息（JSON格式）")
    
    # 时间戳（继承自 BaseModel）
    # created_at: Mapped[datetime]
    # updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, default=None, comment="软删除时间")
    
    # 索引
    __table_args__ = (
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_last_login_time", "last_login_time"),
        Index("idx_users_status", "status"),
    )



