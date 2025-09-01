#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参数验证工具"""

import os
from typing import Dict, Any, List, Optional, Union
import jsonschema
from jsonschema import validate

from src.utils.error_handling import ValidationError
import logging

# 配置日志
schema_logger = logging.getLogger('schema_validator')

def validate_parameters(plot_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证图表参数并返回处理后的参数
    
    Args:
        plot_type: 图表类型
        params: 图表参数字典
        
    Returns:
        处理后的参数字典
        
    Raises:
        ValidationError: 参数验证失败时抛出
    """
    # 确保params是字典
    if not isinstance(params, dict):
        schema_logger.error("参数必须是字典类型")
        raise ValidationError("参数必须是字典类型")
    
    # 基本参数验证
    _check_required_params(plot_type, params)
    
    # 数据字段验证
    if plot_type != 'mermaid_chart' and 'data' in params:
        _validate_data_fields(plot_type, params)
        
    # 特定图表类型的额外验证
    _chart_specific_validations(plot_type, params)
    
    schema_logger.info(f"参数验证通过，图表类型: {plot_type}")
    return params

def _check_required_params(plot_type: str, params: Dict[str, Any]) -> None:
    """检查必需参数
    
    Args:
        plot_type: 图表类型
        params: 图表参数字典
        
    Raises:
        ValidationError: 缺少必需参数时抛出
    """
    # 定义每种图表类型的必需参数
    required_params_map = {
        'line_chart': ['data', 'x_field', 'y_fields'],
        'bar_chart': ['data', 'x_field', 'y_fields'],
        'pie_chart': ['data', 'name_field', 'value_field'],
        'scatter_plot': ['data', 'x_field', 'y_field'],
        'heatmap': ['data', 'x_field', 'y_field', 'value_field'],
        'mermaid_chart': ['mermaid_code']
    }
    
    # 检查图表类型是否支持
    if plot_type not in required_params_map:
        schema_logger.error(f"不支持的图表类型: {plot_type}")
        raise ValidationError(f"不支持的图表类型 '{plot_type}'，支持的类型有: {', '.join(required_params_map.keys())}")
    
    # 检查必需参数是否存在
    required_params = required_params_map[plot_type]
    missing_params = [param for param in required_params if param not in params]
    
    if missing_params:
        schema_logger.error(f"缺少必需参数: {missing_params}")
        params_str = "', '" .join(missing_params)
        raise ValidationError(f"缺少必需参数: '{params_str}'")
    
    # 对某些特殊必需参数进行类型和内容验证
    if plot_type != 'mermaid_chart' and not isinstance(params.get('data'), list):
        schema_logger.error("数据必须是列表类型")
        raise ValidationError("数据必须是列表类型")
    
    if plot_type == 'mermaid_chart' and (not params.get('mermaid_code') or not isinstance(params['mermaid_code'], str)):
        schema_logger.error("Mermaid代码不能为空且必须是字符串类型")
        raise ValidationError("Mermaid代码不能为空且必须是字符串类型")

def _validate_data_fields(plot_type: str, params: Dict[str, Any]) -> None:
    """验证数据中的字段是否存在
    
    Args:
        plot_type: 图表类型
        params: 图表参数字典
        
    Raises:
        ValidationError: 数据字段验证失败时抛出
    """
    data = params['data']
    
    # 检查数据是否为空
    if not data:
        schema_logger.error("数据列表不能为空")
        raise ValidationError("数据列表不能为空")
    
    # 检查数据项是否为字典
    invalid_items = [i for i, item in enumerate(data) if not isinstance(item, dict)]
    if invalid_items:
        schema_logger.error(f"数据项必须是字典类型，无效项索引: {invalid_items}")
        raise ValidationError(f"数据项必须是字典类型，无效项索引: {invalid_items}")
    
    # 图表类型特定的字段验证
    if plot_type in ['line_chart', 'bar_chart', 'scatter_plot', 'heatmap']:
        if 'x_field' in params:
            x_field = params['x_field']
            missing_fields = [i for i, item in enumerate(data) if x_field not in item]
            if missing_fields:
                schema_logger.error(f"数据项中缺少x_field '{x_field}'，缺失索引: {missing_fields}")
                raise ValidationError(f"数据项中缺少x_field '{x_field}'，缺失索引: {missing_fields}")
    
    if plot_type in ['line_chart', 'bar_chart']:
        if 'y_fields' in params:
            y_fields = params['y_fields']
            if not isinstance(y_fields, list):
                schema_logger.error("y_fields必须是字符串列表")
                raise ValidationError("y_fields必须是字符串列表")
            
            for y_field in y_fields:
                missing_fields = [i for i, item in enumerate(data) if y_field not in item]
                if missing_fields:
                    schema_logger.error(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_fields}")
                    raise ValidationError(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_fields}")
    
    if plot_type in ['scatter_plot']:
        if 'y_field' in params:
            y_field = params['y_field']
            missing_fields = [i for i, item in enumerate(data) if y_field not in item]
            if missing_fields:
                schema_logger.error(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_fields}")
                raise ValidationError(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_fields}")
    
    if plot_type in ['pie_chart']:
        if 'name_field' in params and 'value_field' in params:
            name_field = params['name_field']
            value_field = params['value_field']
            
            missing_name = [i for i, item in enumerate(data) if name_field not in item]
            if missing_name:
                schema_logger.error(f"数据项中缺少name_field '{name_field}'，缺失索引: {missing_name}")
                raise ValidationError(f"数据项中缺少name_field '{name_field}'，缺失索引: {missing_name}")
            
            missing_value = [i for i, item in enumerate(data) if value_field not in item]
            if missing_value:
                schema_logger.error(f"数据项中缺少value_field '{value_field}'，缺失索引: {missing_value}")
                raise ValidationError(f"数据项中缺少value_field '{value_field}'，缺失索引: {missing_value}")
    
    if plot_type in ['heatmap']:
        if 'y_field' in params and 'value_field' in params:
            y_field = params['y_field']
            value_field = params['value_field']
            
            missing_y = [i for i, item in enumerate(data) if y_field not in item]
            if missing_y:
                schema_logger.error(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_y}")
                raise ValidationError(f"数据项中缺少y_field '{y_field}'，缺失索引: {missing_y}")
            
            missing_value = [i for i, item in enumerate(data) if value_field not in item]
            if missing_value:
                schema_logger.error(f"数据项中缺少value_field '{value_field}'，缺失索引: {missing_value}")
                raise ValidationError(f"数据项中缺少value_field '{value_field}'，缺失索引: {missing_value}")

def _chart_specific_validations(plot_type: str, params: Dict[str, Any]) -> None:
    """特定图表类型的额外验证
    
    Args:
        plot_type: 图表类型
        params: 图表参数字典
        
    Raises:
        ValidationError: 验证失败时抛出
    """
    # 饼图特定验证
    if plot_type == 'pie_chart' and 'data' in params and 'value_field' in params:
        value_field = params['value_field']
        negative_values = [(i, item[value_field]) for i, item in enumerate(params['data']) 
                          if isinstance(item, dict) and value_field in item and item[value_field] < 0]
        
        if negative_values:
            schema_logger.error(f"饼图数值不能为负数，负值项: {negative_values}")
            error_msg = "饼图数值不能为负数，以下索引项包含负值: " + ", ".join([f"{idx}({val})" for idx, val in negative_values])
            raise ValidationError(error_msg)
    
    # Mermaid图特定验证
    if plot_type == 'mermaid_chart' and 'save_path' in params and params['save_path']:
        ext = os.path.splitext(params['save_path'])[1].lower()[1:]
        if ext not in ['png', 'svg', 'mmd']:
            schema_logger.error(f"不支持的Mermaid图文件格式 '{ext}'")
            raise ValidationError(f"不支持的Mermaid图文件格式 '{ext}'，支持的格式: png, svg, mmd")
    
    # 图表尺寸验证
    if 'figsize' in params and params['figsize']:
        if not isinstance(params['figsize'], list) or len(params['figsize']) != 2:
            schema_logger.error("figsize必须是包含两个数字的列表")
            raise ValidationError("figsize必须是包含两个数字的列表，例如: [10, 6]")
        
        if params['figsize'][0] <= 0 or params['figsize'][1] <= 0:
            schema_logger.error("figsize中的数值必须大于0")
            raise ValidationError("figsize中的数值必须大于0")
    
    # DPI验证
    if 'dpi' in params and params['dpi']:
        if not isinstance(params['dpi'], int) or params['dpi'] <= 0:
            schema_logger.error("dpi必须是大于0的整数")
            raise ValidationError("dpi必须是大于0的整数")

def process_nested_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理嵌套参数，提取内部params并转换数据类型
    
    Args:
        params: 原始参数字典
        
    Returns:
        处理后的参数字典
    """
    # 处理 {'params': {...}} 这种嵌套格式
    if isinstance(params, dict) and 'params' in params:
        processed_params = params['params']
        # 确保processed_params是字典
        if not isinstance(processed_params, dict):
            processed_params = {}
    else:
        processed_params = params.copy() if isinstance(params, dict) else {}
    
    return processed_params

# 保留原有的validate_chart_params函数以保持向后兼容性
def validate_chart_params(chart_type: str, params: Dict[str, Any]) -> bool:
    """
    验证图表参数的便捷函数
    
    参数:
        chart_type: 图表类型
        params: 图表参数
    
    返回:
        是否验证通过
    
    抛出:
        ValidationError: 当参数验证失败时
    """
    validate_parameters(chart_type, params)
    return True