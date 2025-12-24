"""
中间件模块
提供请求处理中间件
"""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from sqlalchemy import event
from sqlalchemy.engine import Engine
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import logger
from src.utils.sql_logger import sql_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录每个请求的详细信息
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())[:8]
        
        # 记录请求开始时间
        start_time = time.time()

        # 记录请求信息
        logger.info(
            f"[{request_id}] 请求开始: {request.method} {request.url.path}"
        )

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = (time.time() - start_time) * 1000

        # 记录响应信息
        logger.info(
            f"[{request_id}] 请求完成: {request.method} {request.url.path} "
            f"状态码={response.status_code} 耗时={process_time:.2f}ms"
        )

        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response


class CatchExceptionMiddleware(BaseHTTPMiddleware):
    """
    异常捕获中间件
    捕获未处理的异常并返回友好的错误信息
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"未处理的异常: {e}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"code": 500, "message": "服务器内部错误", "data": None},
            )


def setup_sql_logging(engine: Engine):
    """
    设置 SQLAlchemy 的 SQL 日志记录
    
    注意：对于异步引擎，需要使用 sync_engine 属性
    
    Args:
        engine: SQLAlchemy 异步引擎
    """
    # 对于异步引擎，使用 sync_engine 来注册事件监听器
    if hasattr(engine, 'sync_engine'):
        sync_engine = engine.sync_engine
    else:
        sync_engine = engine
    
    @event.listens_for(sync_engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """在执行 SQL 之前记录"""
        # 存储开始时间
        conn.info.setdefault("query_start_time", []).append(time.time())
    
    @event.listens_for(sync_engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """在执行 SQL 之后记录"""
        total_time = time.time() - conn.info["query_start_time"].pop(-1)
        
        # 只记录耗时的查询或特定的查询
        execution_time_ms = total_time * 1000
        
        # 记录 SQL 语句
        try:
            # 清理 SQL 语句（移除多余空格）
            clean_sql = " ".join(statement.split())
            sql_logger.log_sql(clean_sql, parameters, execution_time_ms)
        except Exception as e:
            logger.error(f"SQL 日志记录失败: {e}")
    
    @event.listens_for(sync_engine, "handle_error")
    def receive_handle_error(exception_context):
        """捕获 SQL 执行错误"""
        try:
            sql_logger.log_error(
                exception_context.original_exception.__str__(),
                exception_context.original_exception
            )
        except Exception as e:
            logger.error(f"SQL 错误日志记录失败: {e}")

