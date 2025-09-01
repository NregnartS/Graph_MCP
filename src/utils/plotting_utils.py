# -*- coding: utf-8 -*-

import inspect
import traceback
import importlib
# 导入日志配置
from src.utils.logging_config import logger
# 直接导入验证工具
from src.utils.validation_utils import validate_chart_params

# 图表配置类，集中管理图表类型信息
class ChartConfig:
    """图表配置类，集中管理图表类型信息"""
    # 图表必需参数配置
    required_params = {
        'line_chart': ['data', 'x_field', 'y_fields'],
        'bar_chart': ['data', 'x_field', 'y_fields'],
        'scatter_plot': ['data', 'x_field', 'y_field'],
        'pie_chart': ['data', 'name_field', 'value_field'],
        'heatmap': ['data', 'x_field', 'y_field', 'value_field']
    }
    
    # 图表底层类映射
    base_classes = {
        'bar_chart': ('src.charts.bar_chart', 'BarChart'),
        'line_chart': ('src.charts.line_chart', 'LineChart'),
        'pie_chart': ('src.charts.pie_chart', 'PieChart'),
        'scatter_plot': ('src.charts.scatter_plot', 'ScatterPlot'),
        'heatmap': ('src.charts.heatmap', 'HeatMap'),
        'mermaid_chart': ('src.charts.mermaid_chart', 'MermaidChart')
    }


def process_nested_params(params):
    """处理可能的嵌套参数结构"""
    if isinstance(params, dict):
        # 处理嵌套的params结构
        if 'params' in params and len(params) == 1:
            logger.info("检测到嵌套的params结构，提取内部参数")
            return params['params']
        return params
    raise ValueError("参数必须是字典类型")


def validate_parameters(plot_type, params):
    """验证图表参数"""
    try:
        validate_chart_params(plot_type, params)
        logger.debug("参数验证通过")
    except Exception:
        # logger.error(f"参数验证失败: {str(e)}")
        raise


def get_target_function(plot_type, plot_func):
    """获取目标函数及其签名，处理包装函数的情况"""
    target_sig = inspect.signature(plot_func)
    target_func = plot_func
    
    # 特殊处理使用*args和**kwargs的包装函数
    if plot_type in ChartConfig.base_classes:
        try:
            module_name, class_name = ChartConfig.base_classes[plot_type]
            module = __import__(module_name, fromlist=[class_name])
            chart_class = getattr(module, class_name)
            target_func = chart_class.generate
            target_sig = inspect.signature(target_func)
        except Exception as e:
            logger.warning(f"无法获取底层函数签名: {str(e)}")
    
    return target_func, target_sig


def filter_kwargs(params, signature):
    """过滤掉函数不接受的参数"""
    filtered_params = {k: v for k, v in params.items() if k in signature.parameters}
    logger.debug(f"过滤后的参数: {filtered_params}")
    return filtered_params


def check_required_params(plot_type, params):
    """检查必需参数是否存在"""
    if plot_type in ChartConfig.required_params:
        required_params = ChartConfig.required_params[plot_type]
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            raise ValueError(f"缺少必需参数: {', '.join(missing_params)}")


def execute_plotting(plot_func, filtered_params, target_sig):
    """执行绘图函数并处理参数不匹配错误"""
    try:
        return plot_func(**filtered_params)
    except TypeError as e:
        # 提供详细的参数错误信息
        target_params = list(target_sig.parameters.keys())
        provided_params = list(filtered_params.keys())
        unexpected_params = [p for p in provided_params if p not in target_params]
        missing_params = [p for p in target_params if p not in provided_params and target_sig.parameters[p].default == inspect.Parameter.empty]
        
        error_msg = f"参数错误: {str(e)}\n"
        if unexpected_params:
            error_msg += f"意外的参数: {', '.join(unexpected_params)}\n"
        if missing_params:
            error_msg += f"缺少必需参数: {', '.join(missing_params)}\n"
        error_msg += f"可用参数列表: {', '.join(target_params)}"
        
        logger.error(error_msg)
        raise ValueError(error_msg)


def handle_plotting_exception(exception, debug_mode):
    """处理绘图过程中的异常"""
    logger.exception(f"生成图表时发生异常: {str(exception)}")
    stack_trace = traceback.format_exc()
    # logger.debug(f"完整错误堆栈: {stack_trace}")
    
    error_message = f"生成图表失败: {str(exception)}"
    if debug_mode:
        error_message += f"\n{stack_trace}"
    
    return {"status": "error", "message": error_message}