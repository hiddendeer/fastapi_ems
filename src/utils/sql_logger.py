"""
SQL 日志记录模块
记录所有数据库查询语句到文件
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from src.common.config import settings


class SQLLogger:
    """SQL 日志记录器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置 SQL 日志记录器"""
        # 创建 logs 目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志记录器
        logger = logging.getLogger("sql_logger")
        logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 按日期生成日志文件名（自动分割）
        log_file = os.path.join(log_dir, f"sql_{datetime.now().strftime('%Y-%m-%d')}.log")
        
        # 创建文件处理器（按大小轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=30,  # 保留 30 个备份
            encoding="utf-8"
        )
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        
        return logger
    
    def log_sql(self, sql: str, params: dict | None = None, execution_time: float = 0):
        """
        记录 SQL 语句
        
        Args:
            sql: SQL 语句
            params: 查询参数
            execution_time: 执行时间（毫秒）
        """
        if params:
            log_msg = f"SQL: {sql} | Params: {params} | Time: {execution_time:.2f}ms"
        else:
            log_msg = f"SQL: {sql} | Time: {execution_time:.2f}ms"
        
        self.logger.info(log_msg)
    
    def log_error(self, sql: str, error: Exception):
        """
        记录 SQL 执行错误
        
        Args:
            sql: SQL 语句
            error: 异常信息
        """
        self.logger.error(f"SQL Error: {sql} | Exception: {str(error)}")


# 全局 SQL 日志记录器实例
sql_logger = SQLLogger()

