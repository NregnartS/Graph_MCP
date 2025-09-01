# -*- coding: utf-8 -*-

import traceback
import logging
from typing import Optional, Dict, Any

# 获取logger实例
logger = logging.getLogger(__name__)


class PlottingError(Exception):
    """绘图服务基础异常类"""
    def __init__(self, message: str, error_type: str = "general", error_code: str = "PLOT_ERROR", 
                 field_name: Optional[str] = None, expected: Optional[str] = None, 
                 actual: Optional[Any] = None):
        self.message = message
        self.error_type = error_type  # general, validation, generation, io, etc.
        self.error_code = error_code
        self.field_name = field_name  # 相关字段名
        self.expected = expected  # 期望值
        self.actual = actual  # 实际值
        
        # 构建更详细的错误信息
        detailed_message = f"[{error_code}] {message}"
        if field_name:
            detailed_message += f" (字段: {field_name})"
        if expected is not None:
            detailed_message += f" (期望: {expected})"
        if actual is not None:
            detailed_message += f" (实际: {actual})"
        
        super().__init__(detailed_message)
        
    def to_dict(self) -> Dict[str, Any]:
        """将异常信息转换为字典格式"""
        return {
            "error_type": self.error_type,
            "error_code": self.error_code,
            "message": self.message,
            "field_name": self.field_name,
            "expected": self.expected,
            "actual": self.actual
        }


class ValidationError(PlottingError):
    """参数验证错误异常"""
    def __init__(self, message: str, field_name: Optional[str] = None, 
                 expected: Optional[str] = None, actual: Optional[Any] = None):
        super().__init__(
            message=message,
            error_type="validation",
            error_code="VALIDATION_ERROR",
            field_name=field_name,
            expected=expected,
            actual=actual
        )


class ChartGenerationError(PlottingError):
    """图表生成错误异常"""
    def __init__(self, message: str, chart_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="generation",
            error_code="GENERATION_ERROR",
            field_name="chart_type" if chart_type else None,
            actual=chart_type
        )


class FileIOError(PlottingError):
    """文件IO错误异常"""
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(
            message=message,
            error_type="io",
            error_code="FILE_ERROR",
            field_name="file_path" if file_path else None,
            actual=file_path
        )


def handle_exception(exception: Exception, debug_mode: bool = False) -> Dict[str, Any]:
    """统一处理异常并返回标准化的错误响应
    
    Args:
        exception: 捕获的异常
        debug_mode: 是否启用调试模式，调试模式下会包含完整堆栈信息
        
    Returns:
        包含状态和错误信息的字典
    """
    # 记录异常到日志
    logger.exception(f"发生异常: {str(exception)}")
    
    # 获取堆栈信息
    stack_trace = traceback.format_exc()
    
    # 标准化错误响应
    if isinstance(exception, PlottingError):
        # 自定义异常，使用其提供的错误信息
        error_info = exception.to_dict()
        message = str(exception)
    else:
        # 非自定义异常，创建通用错误信息
        error_info = {
            "error_type": "general",
            "error_code": "UNKNOWN_ERROR",
            "message": str(exception)
        }
        message = f"发生未知错误: {str(exception)}"
    
    # 构建响应
    response = {
        "status": "error",
        "message": message,
        "error_info": error_info
    }
    
    # 在调试模式下添加堆栈信息
    if debug_mode:
        response["stack_trace"] = stack_trace
    
    return response


def log_error(operation: str, error: Exception, additional_info: Optional[Dict[str, Any]] = None) -> None:
    """记录错误日志，包含操作信息和额外上下文
    
    Args:
        operation: 操作名称
        error: 错误异常
        additional_info: 额外上下文信息
    """
    log_message = f"操作 '{operation}' 失败: {str(error)}"
    
    # 如果有额外信息，添加到日志
    if additional_info:
        log_details = ", ".join([f"{k}={v}" for k, v in additional_info.items()])
        log_message += f" [详情: {log_details}]"
    
    # 根据错误类型记录不同级别的日志
    if isinstance(error, ValidationError):
        logger.warning(log_message)
    else:
        logger.error(log_message)


# 导出主要类和函数
__all__ = [
    "PlottingError",
    "ValidationError",
    "ChartGenerationError",
    "FileIOError",
    "handle_exception",
    "log_error"
]