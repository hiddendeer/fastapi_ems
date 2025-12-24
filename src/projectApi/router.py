import asyncio
import re
from typing import Any

from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas import ResponseModel
from src.projectApi.service import get_users
from src.projectApi.schemas import UserResponse

router = APIRouter(prefix="/projectApi", tags=["ProjectApi"])

@router.get("/info")
async def get_project_info(
    just_id: str = Query(None, description="JustID"),
    db: AsyncSession = Depends(get_db),
) -> ResponseModel:
    """获取项目列表"""
    print(just_id,"just_id")
    result = await get_users(db=db)
    result_handle = result.get("data",[])
    for item in result_handle:
        print(item.get("nickname"),111)
    return ResponseModel(
        code=200,
        message="success",
        data=result_handle
    )