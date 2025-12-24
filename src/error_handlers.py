"""
全局异常处理
统一错误响应格式
"""
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ValidationError

from src.schemas import ErrorResponse


# 中文验证错误信息映射
VALIDATION_ERROR_MESSAGES = {
    "greater_than_equal": "必须大于等于 {ge}",
    "greater_than": "必须大于 {gt}",
    "less_than_equal": "必须小于等于 {le}",
    "less_than": "必须小于 {lt}",
    "string_too_short": "长度不能少于 {min_length} 个字符",
    "string_too_long": "长度不能超过 {max_length} 个字符",
    "int_parsing": "必须是整数",
    "float_parsing": "必须是数字",
    "string_type": "必须是字符串",
    "list_type": "必须是列表",
    "dict_type": "必须是字典",
    "bool_type": "必须是布尔值",
    "missing": "此字段必填",
    "extra_forbidden": "不允许的字段",
}


def get_chinese_error_message(error: dict) -> str:
    """
    将 Pydantic 验证错误转换为中文错误消息
    
    Args:
        error: Pydantic 验证错误字典
    
    Returns:
        中文错误消息
    """
    error_type = error.get("type", "")
    ctx = error.get("ctx", {})
    field = error.get("loc", ["unknown"])[-1]  # 获取字段名
    
    # 获取基础错误消息
    base_message = VALIDATION_ERROR_MESSAGES.get(error_type, error.get("msg", "参数错误"))
    
    # 替换占位符
    if "{ge}" in base_message and "ge" in ctx:
        base_message = base_message.replace("{ge}", str(ctx["ge"]))
    if "{gt}" in base_message and "gt" in ctx:
        base_message = base_message.replace("{gt}", str(ctx["gt"]))
    if "{le}" in base_message and "le" in ctx:
        base_message = base_message.replace("{le}", str(ctx["le"]))
    if "{lt}" in base_message and "lt" in ctx:
        base_message = base_message.replace("{lt}", str(ctx["lt"]))
    if "{min_length}" in base_message and "min_length" in ctx:
        base_message = base_message.replace("{min_length}", str(ctx["min_length"]))
    if "{max_length}" in base_message and "max_length" in ctx:
        base_message = base_message.replace("{max_length}", str(ctx["max_length"]))
    
    return f"字段 '{field}': {base_message}"


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置全局异常处理器
    
    Args:
        app: FastAPI 应用实例
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        """
        处理 Pydantic 验证错误
        将其转换为统一的错误格式
        """
        errors = exc.errors()
        
        # 获取第一个错误的中文描述
        if errors:
            error_message = get_chinese_error_message(errors[0])
        else:
            error_message = "请求参数验证失败"
        
        # 返回统一的错误格式
        error_response = ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="error",
            errorMessage=error_message,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """
        处理未捕获的异常
        """
        error_response = ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="error",
            errorMessage=str(exc) or "服务器内部错误",
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )

