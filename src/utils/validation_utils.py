#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import jsonschema
from jsonschema import validate
from typing import Dict, Any, List, Optional, Union, Tuple

# 获取logger实例
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """参数验证错误异常"""
    pass


class SchemaValidator:
    """参数验证器"""
    
    def __init__(self):
        # 定义各种图表类型的JSON Schema
        self.schemas = {
            'line_chart': {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "minItems": 1
                    },
                    "x_field": {"type": "string", "minLength": 1},
                    "y_fields": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "minItems": 1
                    },
                    "title": {"type": "string"},
                    "x_label": {"type": ["string", "null"]},
                    "y_label": {"type": ["string", "null"]},
                    "colors": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "line_styles": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "line_widths": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 0}
                    },
                    "markers": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "theme": {"type": "string"},
                    "save_path": {"type": ["string", "null"]},
                    "figsize": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "dpi": {"type": ["integer", "null"], "minimum": 1},
                    "grid": {"type": ["boolean", "null"]}
                },
                "required": ["data", "x_field", "y_fields"]
            },
            'bar_chart': {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "minItems": 1
                    },
                    "x_field": {"type": "string", "minLength": 1},
                    "y_fields": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "minItems": 1
                    },
                    "title": {"type": "string"},
                    "x_label": {"type": ["string", "null"]},
                    "y_label": {"type": ["string", "null"]},
                    "colors": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "bar_width": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                    "stack": {"type": ["boolean", "null"]},
                    "edge_color": {"type": ["string", "null"]},
                    "edge_width": {"type": ["number", "null"], "minimum": 0},
                    "horizontal": {"type": ["boolean", "null"]},
                    "theme": {"type": "string"},
                    "save_path": {"type": ["string", "null"]},
                    "figsize": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "dpi": {"type": ["integer", "null"], "minimum": 1},
                    "grid": {"type": ["boolean", "null"]}
                },
                "required": ["data", "x_field", "y_fields"]
            },
            'pie_chart': {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "minItems": 1
                    },
                    "name_field": {"type": "string", "minLength": 1},
                    "value_field": {"type": "string", "minLength": 1},
                    "title": {"type": "string"},
                    "explode": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 0}
                    },
                    "autopct": {"type": ["string", "null"]},
                    "start_angle": {"type": ["number", "null"]},
                    "shadow": {"type": ["boolean", "null"]},
                    "labeldistance": {"type": ["number", "null"], "minimum": 0},
                    "colors": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "theme": {"type": "string"},
                    "save_path": {"type": ["string", "null"]},
                    "figsize": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "dpi": {"type": ["integer", "null"], "minimum": 1},
                    "legend": {"type": ["boolean", "null"]},
                    "legend_loc": {"type": ["string", "null"]}
                },
                "required": ["data", "name_field", "value_field"]
            },
            'scatter_plot': {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "minItems": 1
                    },
                    "x_field": {"type": "string", "minLength": 1},
                    "y_field": {"type": "string", "minLength": 1},
                    "title": {"type": "string"},
                    "x_label": {"type": ["string", "null"]},
                    "y_label": {"type": ["string", "null"]},
                    "color_field": {"type": ["string", "null"]},
                    "size_field": {"type": ["string", "null"]},
                    "color_map": {"type": ["string", "null"]},
                    "marker_style": {"type": ["string", "null"]},
                    "alpha": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                    "theme": {"type": "string"},
                    "save_path": {"type": ["string", "null"]},
                    "figsize": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "dpi": {"type": ["integer", "null"], "minimum": 1},
                    "grid": {"type": ["boolean", "null"]}
                },
                "required": ["data", "x_field", "y_field"]
            },
            'heatmap': {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "minItems": 1
                    },
                    "x_field": {"type": "string", "minLength": 1},
                    "y_field": {"type": "string", "minLength": 1},
                    "value_field": {"type": "string", "minLength": 1},
                    "title": {"type": "string"},
                    "x_label": {"type": ["string", "null"]},
                    "y_label": {"type": ["string", "null"]},
                    "color_map": {"type": ["string", "null"]},
                    "annotate": {"type": ["boolean", "null"]},
                    "fmt": {"type": ["string", "null"]},
                    "linewidths": {"type": ["number", "null"], "minimum": 0},
                    "linecolor": {"type": ["string", "null"]},
                    "aggregation": {"type": ["string", "null"], "enum": ["mean", "sum", "max", "min", "count"]},
                    "cbar_kws": {"type": ["object", "null"]},
                    "theme": {"type": "string"},
                    "save_path": {"type": ["string", "null"]},
                    "figsize": {
                        "type": ["array", "null"],
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "dpi": {"type": ["integer", "null"], "minimum": 1}
                },
                "required": ["data", "x_field", "y_field", "value_field"]
            },
            'mermaid_chart': {
                "type": "object",
                "properties": {
                    "mermaid_code": {"type": "string", "minLength": 1},
                    "save_path": {"type": ["string", "null"]},
                    "theme": {"type": "string", "enum": ["default", "dark", "forest", "neutral"]},
                    "width": {"type": ["integer", "null"], "minimum": 1},
                    "height": {"type": ["integer", "null"], "minimum": 1}
                },
                "required": ["mermaid_code"]
            }
        }
    
    def validate_params(self, chart_type: str, params: Dict[str, Any]) -> bool:
        """
        验证图表参数
        
        参数:
            chart_type: 图表类型
            params: 图表参数
        
        返回:
            是否验证通过
        
        抛出:
            ValidationError: 当参数验证失败时
        """
        try:
            # 检查图表类型是否支持
            if chart_type not in self.schemas:
                raise ValidationError(f"不支持的图表类型: {chart_type}")
            
            # 获取对应的schema
            schema = self.schemas[chart_type]
            
            # 执行验证
            validate(instance=params, schema=schema)
            
            # 执行额外的数据字段检查
            if 'data' in params and chart_type != 'mermaid_chart':
                data = params['data']
                
                # 检查数据字段是否存在
                if chart_type in ['line_chart', 'bar_chart', 'scatter_plot', 'heatmap']:
                    if 'x_field' in params:
                        x_field = params['x_field']
                        if not all(x_field in item for item in data if isinstance(item, dict)):
                            raise ValidationError("数据项中缺少指定的字段")
                
                if chart_type in ['line_chart', 'bar_chart']:
                    if 'y_fields' in params:
                        for y_field in params['y_fields']:
                            if not all(y_field in item for item in data if isinstance(item, dict)):
                                raise ValidationError("数据项中缺少指定的字段")
                
                if chart_type in ['scatter_plot']:
                    if 'y_field' in params:
                        y_field = params['y_field']
                        if not all(y_field in item for item in data if isinstance(item, dict)):
                            raise ValidationError("数据项中缺少指定的字段")
                
                if chart_type in ['pie_chart']:
                    if 'name_field' in params and 'value_field' in params:
                        name_field = params['name_field']
                        value_field = params['value_field']
                        if not all(name_field in item and value_field in item for item in data if isinstance(item, dict)):
                            raise ValidationError("数据项中缺少指定的字段")
                
                if chart_type in ['heatmap']:
                    if 'y_field' in params and 'value_field' in params:
                        y_field = params['y_field']
                        value_field = params['value_field']
                        if not all(y_field in item and value_field in item for item in data if isinstance(item, dict)):
                            raise ValidationError("数据项中缺少指定的字段")
            
            # 饼图特定验证
            if chart_type == 'pie_chart' and 'data' in params:
                for item in params['data']:
                    if isinstance(item, dict) and 'value_field' in params:
                        value_field = params['value_field']
                        if value_field in item and item[value_field] < 0:
                            raise ValidationError("饼图数值不能为负数")
            
            # Mermaid图特定验证
            if chart_type == 'mermaid_chart' and 'save_path' in params and params['save_path']:
                ext = os.path.splitext(params['save_path'])[1].lower()[1:]
                if ext not in ['png', 'svg', 'mmd']:
                    raise ValidationError(f"不支持的文件格式 '{ext}'，支持的格式: png, svg, mmd")
            
            return True
        except jsonschema.exceptions.ValidationError as e:
            # 格式化错误信息
            error_path = '.'.join(map(str, e.path)) if e.path else "root"
            
            # 根据错误类型提供更友好的错误消息
            if e.validator == 'required':
                # 使用不同的引号方式避免嵌套问题
                error_msg = "缺少必填参数 '" + e.message.split("'" )[1] + "'"
            elif chart_type == 'line_chart' and e.path and str(e.path[0]) == 'data':
                error_msg = "不是有效的数据列表"
            elif chart_type == 'mermaid_chart' and e.path and str(e.path[0]) == 'mermaid_code':
                error_msg = "Mermaid代码不能为空"
            else:
                error_msg = f"参数验证失败 ({error_path}): {e.message}"
            
            # logger.error(error_msg)
            raise ValidationError(error_msg) from e
        except Exception as e:
            error_msg = f"验证参数时发生错误: {str(e)}"
            # logger.error(error_msg)
            raise ValidationError(error_msg) from e


# 创建全局验证器实例
validator = SchemaValidator()

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
    # validate_params方法现在会在验证失败时直接抛出ValidationError
    # 所以这里只需要调用它并返回True
    validator.validate_params(chart_type, params)
    return True