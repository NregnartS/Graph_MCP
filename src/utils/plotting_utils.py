# -*- coding: utf-8 -*-

import inspect
import traceback
import importlib
from typing import Dict, Any, Tuple, Optional, Callable, Union

# 导入日志配置
from src.utils.logging_config import logger
# 直接导入验证工具
from src.utils.validation_utils import validate_parameters as validate_chart_params, process_nested_params as process_nested_params_util
# 导入错误处理类
from src.utils.error_handling import ValidationError, ChartGenerationError, handle_exception

class ChartConfig:
    """图表配置类，集中管理图表类型信息和扩展点"""
    
    def __init__(self):
        # 初始化图表类型配置
        self._chart_types = {
            'bar_chart': {
                'module': 'src.charts.bar_chart',
                'class_name': 'BarChart',
                'required_params': ['data', 'x_field', 'y_fields']
            },
            'line_chart': {
                'module': 'src.charts.line_chart',
                'class_name': 'LineChart',
                'required_params': ['data', 'x_field', 'y_fields']
            },
            'pie_chart': {
                'module': 'src.charts.pie_chart',
                'class_name': 'PieChart',
                'required_params': ['data', 'name_field', 'value_field']
            },
            'scatter_plot': {
                'module': 'src.charts.scatter_plot',
                'class_name': 'ScatterPlot',
                'required_params': ['data', 'x_field', 'y_field']
            },
            'heatmap': {
                'module': 'src.charts.heatmap',
                'class_name': 'HeatMap',
                'required_params': ['data', 'x_field', 'y_field', 'value_field']
            },
            'mermaid_chart': {
                'module': 'src.charts.mermaid_chart',
                'class_name': 'MermaidChart',
                'required_params': ['mermaid_code']
            }
        }
        
    @property
    def supported_chart_types(self) -> list:
        """获取所有支持的图表类型"""
        return list(self._chart_types.keys())
        
    def is_supported(self, chart_type: str) -> bool:
        """检查图表类型是否支持"""
        return chart_type in self._chart_types
        
    def get_chart_config(self, chart_type: str) -> Dict[str, Any]:
        """获取图表类型的配置信息"""
        if not self.is_supported(chart_type):
            supported_types = ', '.join(self.supported_chart_types)
            raise ValueError(f"不支持的图表类型: {chart_type}。支持的类型有: {supported_types}")
        return self._chart_types[chart_type]
        
    def get_required_params(self, chart_type: str) -> list:
        """获取图表类型的必需参数列表"""
        config = self.get_chart_config(chart_type)
        return config.get('required_params', [])
        
    def get_chart_class(self, chart_type: str) -> type:
        """动态加载并返回图表类"""
        config = self.get_chart_config(chart_type)
        try:
            module = importlib.import_module(config['module'])
            chart_class = getattr(module, config['class_name'])
            return chart_class
        except ImportError as e:
            logger.error(f"无法导入图表模块 {config['module']}: {str(e)}")
            raise ChartGenerationError(f"无法加载图表类型 '{chart_type}' 的实现模块") from e
        except AttributeError as e:
            logger.error(f"在模块 {config['module']} 中找不到类 {config['class_name']}: {str(e)}")
            raise ChartGenerationError(f"无法找到图表类型 '{chart_type}' 的实现类") from e
            
    def register_chart_type(self, chart_type: str, module_path: str, class_name: str, required_params: list) -> None:
        """注册新的图表类型，用于扩展功能"""
        if self.is_supported(chart_type):
            logger.warning(f"图表类型 '{chart_type}' 已存在，将被覆盖")
        
        self._chart_types[chart_type] = {
            'module': module_path,
            'class_name': class_name,
            'required_params': required_params
        }
        logger.info(f"成功注册新的图表类型: {chart_type}")

# 创建全局ChartConfig实例
chart_config = ChartConfig()


def process_nested_params(params: Any) -> Dict[str, Any]:
    """处理可能的嵌套参数结构"""
    try:
        result = process_nested_params_util(params)
        logger.debug("参数嵌套结构处理完成")
        return result
    except Exception as e:
        logger.error(f"处理嵌套参数时出错: {str(e)}")
        raise ValidationError(f"参数格式错误: {str(e)}") from e


def validate_parameters(plot_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证图表参数"""
    try:
        result = validate_chart_params(plot_type, params)
        logger.debug(f"图表类型 '{plot_type}' 的参数验证通过")
        return result
    except ValidationError:
        # 已经在validate_chart_params中记录了日志，这里直接重新抛出
        raise
    except Exception as e:
        logger.error(f"参数验证过程中发生未预期错误: {str(e)}")
        raise ValidationError(f"参数验证失败: {str(e)}") from e


def get_target_function(plot_type: str, plot_func: Optional[Callable] = None) -> Tuple[Callable, inspect.Signature]:
    """获取目标函数及其签名，处理包装函数的情况"""
    try:
        # 如果提供了plot_func，先使用它
        if plot_func:
            target_func = plot_func
            target_sig = inspect.signature(target_func)
        else:
            # 否则从chart_config获取并实例化图表类
            chart_class = chart_config.get_chart_class(plot_type)
            # 实例化图表类
            chart_instance = chart_class()
            # 获取实例的generate方法
            target_func = chart_instance.generate
            target_sig = inspect.signature(target_func)
            
        logger.debug(f"获取图表类型 '{plot_type}' 的目标函数成功")
        return target_func, target_sig
    except Exception as e:
        logger.error(f"获取目标函数时出错: {str(e)}")
        raise ChartGenerationError(f"无法获取图表生成函数: {str(e)}") from e


def filter_kwargs(params: Dict[str, Any], signature: inspect.Signature) -> Dict[str, Any]:
    """过滤掉函数不接受的参数"""
    # 获取签名中的参数名列表
    valid_param_names = list(signature.parameters.keys())
    # 过滤参数
    filtered_params = {k: v for k, v in params.items() if k in valid_param_names}
    
    # 检查是否有被过滤掉的参数并记录日志
    filtered_keys = [k for k in params.keys() if k not in valid_param_names]
    if filtered_keys:
        logger.debug(f"过滤掉不支持的参数: {filtered_keys}")
    
    logger.debug(f"过滤后的参数: {filtered_params}")
    return filtered_params


def execute_plotting(plot_func: Callable, filtered_params: Dict[str, Any], target_sig: inspect.Signature) -> Any:
    """执行绘图函数并处理参数不匹配错误"""
    try:
        logger.debug("开始执行图表生成函数")
        result = plot_func(**filtered_params)
        logger.info("图表生成成功")
        return result
    except TypeError as e:
        # 提供详细的参数错误信息
        target_params = list(target_sig.parameters.keys())
        provided_params = list(filtered_params.keys())
        unexpected_params = [p for p in provided_params if p not in target_params]
        missing_params = [p for p in target_params 
                         if p not in provided_params 
                         and target_sig.parameters[p].default == inspect.Parameter.empty]
        
        error_msg = f"参数错误: {str(e)}\n"
        if unexpected_params:
            error_msg += f"意外的参数: {', '.join(unexpected_params)}\n"
        if missing_params:
            error_msg += f"缺少必需参数: {', '.join(missing_params)}\n"
        error_msg += f"可用参数列表: {', '.join(target_params)}"
        
        logger.error(error_msg)
        raise ValidationError(error_msg) from e
    except Exception as e:
        logger.error(f"执行图表生成函数时发生错误: {str(e)}")
        raise ChartGenerationError(f"图表生成失败: {str(e)}") from e


def handle_plotting_exception(exception: Exception, debug_mode: bool = False) -> Dict[str, str]:
    """处理绘图过程中的异常"""
    # 使用统一的错误处理函数
    error_info = handle_exception(exception, debug_mode)
    
    # 格式化为MCP服务需要的响应格式
    return error_info


def get_chart_instance(chart_type: str, **kwargs) -> Any:
    """获取图表实例"""
    try:
        chart_class = chart_config.get_chart_class(chart_type)
        instance = chart_class(**kwargs)
        logger.debug(f"创建图表类型 '{chart_type}' 的实例成功")
        return instance
    except Exception as e:
        logger.error(f"创建图表实例时出错: {str(e)}")
        raise ChartGenerationError(f"无法创建图表实例: {str(e)}") from e


# 全局变量，用于跟踪字体是否已设置
_fonts_initialized = False

def setup_chart_theme(theme: Optional[str] = None) -> None:
    """设置图表主题
    
    注意：字体设置只在首次调用时执行，之后不再重复设置
    """
    global _fonts_initialized
    
    try:
        # 只在首次调用时设置字体
        if not _fonts_initialized:
            # 导入字体设置工具
            from src.utils.font_utils import set_matplotlib_fonts
            
            # 设置中文字体
            set_matplotlib_fonts()
            _fonts_initialized = True
        
        # 如果指定了主题，应用主题
        if theme:
            import matplotlib.pyplot as plt
            # 检查主题是否存在
            if theme in plt.style.available:
                plt.style.use(theme)
                logger.debug(f"应用图表主题: {theme}")
            elif theme == 'default':
                # 'default'是特殊主题，使用matplotlib默认设置
                plt.style.use('default')
                logger.debug("使用默认主题")
            else:
                logger.warning(f"主题 '{theme}' 不可用，使用默认主题")
        
    except Exception as e:
        logger.error(f"设置图表主题时出错: {str(e)}")
        # 不抛出异常，继续使用默认设置