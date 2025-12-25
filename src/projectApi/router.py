import asyncio
import re
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db
from src.common.schemas import ResponseModel
from src.projectApi.service import get_users, get_user_id
from src.projectApi.schemas import UserResponse

router = APIRouter(prefix="/projectApi", tags=["ProjectApi"])

@router.get("/info")
async def get_project_info(
    just_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
) -> ResponseModel:
    """获取用户信息"""
    
    try:
        # 1. 验证参数
        if not just_id:
            return ResponseModel(
                code=400,
                message="缺少必需参数：just_id",
                data={}
            )
        
        # 2. 获取用户列表
        result = await get_users(db=db)
        result_handle = result.get("data", [])
        
        # 3. 获取指定用户信息
        result_obj = await get_user_id(db=db, user_id=int(just_id))
        
        # 4. 安全检查：用户是否存在
        if result_obj is None:
            return ResponseModel(
                code=404,
                message=f"用户不存在：{just_id}",
                data=None
            )

        list_info = {"a": 1}
        if not list_info:
            print("list_info is empty")

        if "a" in list_info:
            print("a is in list_info")
        
        # 5. 安全检查：用户列表是否为空
        if not result_handle:
            return ResponseModel(
                code=200,
                message="success",
                data={
                    "user_info": result_obj,
                    "user_list": []
                }
            )
        
        # 6. 安全获取用户昵称（提供默认值）
        user_nickname = result_obj.get("nickname") or "未设置昵称"
        
        # 7. 更新列表中第一个用户的昵称（安全方式）
        result_handle[0]["nickname"] = user_nickname
        
        return ResponseModel(
            code=200,
            message="success",
            data={
                "user_info": result_obj,
                "user_list": result_handle
            }
        )
        
    except ValueError as e:
        # 处理 just_id 转整数失败
        return ResponseModel(
            code=400,
            message=f"参数类型错误：just_id 必须是整数，收到：{just_id}",
            data=None
        )
    except Exception as e:
        # 捕获所有其他异常
        return ResponseModel(
            code=500,
            message=f"服务器错误：{str(e)}",
            data=None
        )