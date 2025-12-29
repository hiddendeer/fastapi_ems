import asyncio
from datetime import datetime
from typing import Any, List, Optional, Dict

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Path,
    Body,
    Header,
    Cookie,
    HTTPException,
    status,
    BackgroundTasks,
    File,
    UploadFile,
    Form,
    Request
)
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db
from src.common.schemas import ResponseModel
from src.projectApi.service import get_users, get_user_id, create_user_raw
from src.projectApi.schemas import UserResponse, UserCreate

# 1. 初始化 APIRouter
# prefix: 路由前缀，tags: 自动生成文档的分组标签
router = APIRouter(prefix="/projectApi", tags=["FastAPI核心核心学习接口"])

# ==========================================
# 2. Pydantic 模型 (Schemas) - 核心知识点 1
# ==========================================

class NestedItem(BaseModel):
    """嵌套模型，展示复杂数据结构"""
    item_id: int = Field(..., description="子项ID")
    item_name: str = Field(..., min_length=1, max_length=50, description="子项名称")

class AdvancedRequest(BaseModel):
    """
    复杂请求模型
    Field(...) 表示必填，Field(None) 表示可选
    ge/le: 数值范围控制，min_length/max_length: 字符串长度控制
    """
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr = Field(..., description="用户邮箱，Pydantic 自动校验格式")
    age: int = Field(18, ge=0, le=150, description="年龄，带默认值")
    tags: List[str] = Field(default=[], description="标签列表")
    metadata: Dict[str, Any] = Field(default={}, description="扩展元数据")
    items: List[NestedItem] = Field(..., description="嵌套列表结构")

    # Pydantic 配置类
    class Config:
        # 允许从 ORM 模型直接转化
        from_attributes = True
        # 文档示例
        json_schema_extra = {
            "example": {
                "username": "fastapi_master",
                "email": "master@example.com",
                "age": 25,
                "tags": ["python", "backend"],
                "items": [{"item_id": 1, "item_name": "Demo Item"}]
            }
        }

# ==========================================
# 3. 依赖注入 (Dependencies) - 核心知识点 2
# ==========================================

# (1) 函数依赖：常用做参数处理、公共逻辑提取
async def common_parameters(
    q: Optional[str] = Query(None, description="全局搜索关键词"),
    page: int = Query(1, ge=1, description="分页页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
):
    return {"q": q, "page": page, "size": size}

# (2) 类依赖：适合需要维护状态或进行复杂初始化的场景
class UserContext:
    def __init__(self, platform: str = Header("web", description="来源平台")):
        self.platform = platform
    
    def get_platform_info(self):
        return f"Request from {self.platform}"

# (3) 权限校验伪造逻辑（子依赖示例）
async def verify_token(x_token: str = Header(..., convert_underscores=False, description="模拟 Token 校验")):
    if x_token != "super-secret-token":
        # 抛出 HTTPException 是 FastAPI 处理错误的推荐方式
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌，请使用 'super-secret-token'"
        )
    return x_token

# ==========================================
# 4. 复杂核心接口示例
# ==========================================

@router.post(
    "/advanced-learning/",
    response_model=ResponseModel, # 指定响应模型，自动递归校验和序列化
    status_code=status.HTTP_201_CREATED, # 定义成功返回的状态码
    summary="FastAPI 核心技术综合演示接口",
    description="这个接口集成了：路径参数、查询参数、请求体、Header、Cookie、依赖注入、后台任务、文件上传等核心技术。"
)
async def core_learning_endpoint(
    # A. 路径参数 (Path Parameters)
    user_id: str = Query(..., description="用户唯一标识，必须大于等于1"),
    
    # B. 请求体 (Request Body) - 自动解析 JSON
    payload: AdvancedRequest = Body(..., description="复杂的 JSON 负载"),
    
    # C. 查询参数 (Query Parameters) - 提取分页和搜索信息
    commons: dict = Depends(common_parameters),
    
    # D. 头部和 Cookie (Header & Cookie)
    user_agent: str = Header(None),
    session_id: Optional[str] = Cookie(None),
    session_card: Optional[str] = Cookie(None),
    
    # E. 依赖注入 (Dependencies)
    ctx: UserContext = Depends(UserContext),
    token: str = Depends(verify_token), # 权限检查
    db: AsyncSession = Depends(get_db), # 数据库会话
    
    # F. 后台任务 (Background Tasks)
    background_tasks: BackgroundTasks = None
):
    """
    接口的主逻辑。
    """
    # 模拟业务处理
    print(f"当前平台: {ctx.get_platform_info()}")
    print(f"Token 验证通过: {token}")
    
    # 后台任务演示：接口不需要等待此任务完成即可返回
    async def log_activity(username: str):
        await asyncio.sleep(2) # 模拟耗时操作
        print(f"日志记录: 用户 {username} 完成了高级演示调用")
    
    if background_tasks:
        background_tasks.add_task(log_activity, payload.username)

    # 业务逻辑：查询数据库示例（复用现有 service）
    # user_data = await get_user_id(db=db, user_id=user_id)

    # 构造返回内容
    result = {
        "received_params": {
            "user_id": user_id,
            "query": commons,
            "headers": {"user_agent": user_agent},
            "cookies": {"session_id": session_id, "session_card": session_card}
        },
        "payload_echo": payload.model_dump(),
        "platform_context": ctx.get_platform_info(),
        "server_time": datetime.now().isoformat()
    }

    return ResponseModel(
        code=200,
        message="恭喜通过核心知识点学习！",
        data=result
    )

# ==========================================
# 5. 其他常用接口形态展示
# ==========================================

@router.post("/upload-logic", summary="文件上传 + 表单字段")
async def upload_demo(
    # File 用于接收文件二进制，UploadFile 包含文件名、内容类型等元数据
    file: UploadFile = File(..., description="上传的头像或文档"),
    # Form 用于接收表单字段 (multipart/form-data)
    title: str = Form(..., description="文件标题"),
    # 校验
    db: AsyncSession = Depends(get_db)
):
    """
    展示如何同时接收文件和表单数据
    """
    content = await file.read() # 异步读取文件内容
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "title": title,
        "file_size_kb": len(content) / 1024
    }

# ==========================================
# 6. 异常处理演示
# ==========================================

@router.get("/error-demo/{code}", summary="异常处理演示")
async def trigger_error(code: int):
    """
    手动抛出不同状态码的异常
    """
    if code == 400:
        raise HTTPException(status_code=400, detail="典型的客户端错误")
    if code == 403:
        raise HTTPException(status_code=403, detail="没有访问权限")
    if code == 500:
        raise HTTPException(status_code=500, detail="服务器内部炸了")
    
    return {"message": "一切正常", "input_code": code}

# ==========================================
# 7. 原生 SQL 接口演示
# ==========================================
from src.projectApi.service import get_user_stats_raw

@router.get("/sql-demo/{user_id}", summary="原生 SQL 查询演示")
async def sql_learning_demo(
    user_id: int = Path(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    展示如何在接口中调用原生 SQL 逻辑
    """
    stats = await get_user_stats_raw(db, user_id)
    
    if not stats:
        return ResponseModel(code=404, message="未找到对应的 SQL 数据统计", data=None)

    return ResponseModel(
        code=200, 
        message="原生 SQL 查询成功！", 
        data=stats
    )

@router.post("/create-user", summary="创建用户")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user_raw(db, user)

# 原有逻辑保留/重构供参考
@router.get("/info", summary="原有用户信息查询接口", deprecated=True)
async def get_project_info(
    just_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
) -> ResponseModel:
    """这里保留原有的简单逻辑，可以和上面的 Complex 接口做对比学习"""
    try:
        user_id_int = int(just_id)
        result_obj = await get_user_id(db=db, user_id=user_id_int)
        
        if result_obj is None:
            return ResponseModel(code=404, message="用户不存在", data=None)

        return ResponseModel(code=200, message="success", data=result_obj)
    except Exception as e:
        return ResponseModel(code=500, message=str(e), data=None)
