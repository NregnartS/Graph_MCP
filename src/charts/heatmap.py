#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from src.plotting_base import PlottingBase

# 获取logger实例
logger = logging.getLogger(__name__)


class HeatMap(PlottingBase):
    """热力图生成器"""
    
    def __init__(self):
        super().__init__()
    
    def generate(
        self,
        data: List[Dict[str, Any]],
        x_field: str,
        y_field: str,
        value_field: str,
        title: str = "热力图",
        x_label: str = None,
        y_label: str = None,
        color_map: str = 'viridis',
        annotate: bool = True,
        fmt: str = '.2f',
        linewidths: float = 0.5,
        linecolor: str = 'white',
        aggregation: str = 'mean',
        cbar_kws: Dict[str, Any] = None,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (10, 8),
        dpi: int = 100
    ) -> str:
        """
        生成热力图
        
        参数:
            data: 数据列表
            x_field: X轴字段名
            y_field: Y轴字段名
            value_field: 数值字段名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color_map: 颜色映射
            annotate: 是否显示数值
            fmt: 数值格式
            linewidths: 网格线宽度
            linecolor: 网格线颜色
            aggregation: 聚合函数，可选值: 'mean', 'sum', 'max', 'min', 'count'
            cbar_kws: 颜色条参数
            theme: 图表主题
            save_path: 保存路径
            figsize: 图形大小
            dpi: 图像分辨率
        
        返回:
            文件路径
        """
        try:
            # 验证必要参数
            if not data:
                raise ValueError("数据不能为空")
            if not x_field:
                raise ValueError("X轴字段名不能为空")
            if not y_field:
                raise ValueError("Y轴字段名不能为空")
            if not value_field:
                raise ValueError("数值字段名不能为空")
            
            df = pd.DataFrame(data)
            
            # 检查字段是否存在
            if x_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{x_field}'")
            if y_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{y_field}'")
            if value_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{value_field}'")
            
            # 支持的聚合函数
            aggregation_funcs = {
                'mean': np.mean,
                'sum': np.sum,
                'max': np.max,
                'min': np.min,
                'count': len
            }
            
            if aggregation not in aggregation_funcs:
                raise ValueError(f"不支持的聚合函数 '{aggregation}'，支持的有: {', '.join(aggregation_funcs.keys())}")
            
            # 创建透视表
            pivot_table = df.pivot_table(
                values=value_field,
                index=y_field,
                columns=x_field,
                aggfunc=aggregation_funcs[aggregation]
            )
            
            # 设置主题
            self._set_theme(theme)
            
            # 创建图形
            plt.figure(figsize=figsize, dpi=dpi)
            ax = plt.gca()
            
            # 绘制热力图
            if cbar_kws is None:
                cbar_kws = {}
            
            sns.heatmap(
                pivot_table,
                annot=annotate,
                fmt=fmt,
                cmap=color_map,
                linewidths=linewidths,
                linecolor=linecolor,
                ax=ax,
                cbar_kws=cbar_kws
            )
            
            # 设置标题和标签
            ax.set_title(title, fontsize=16)
            
            # 调整x轴和y轴标签
            if x_label:
                ax.set_xlabel(x_label, fontsize=12)
            
            if y_label:
                ax.set_ylabel(y_label, fontsize=12)
            
            # 设置刻度字体大小
            ax.tick_params(axis='both', labelsize=10)
            
            # 调整x轴标签旋转
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45 if len(pivot_table.columns) > 5 else 0, ha='right')
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
            
            # 调整注释文本样式
            if annotate:
                for text in ax.texts:
                    text.set_fontsize(10)
                    # 设置文本颜色，根据背景色决定
                    # 先检查bbox_patch是否存在
                    if text.get_bbox_patch() is not None:
                        bg_color = text.get_bbox_patch().get_facecolor()
                        # 计算背景色亮度
                        brightness = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
                        text.set_color('white' if brightness < 0.5 else 'black')
            
            plt.tight_layout()
            
            # 保存图表
            return self._save_plot(save_path, "heatmap")
        except Exception as e:
            logger.error(f"生成热力图失败: {str(e)}")
            # 确保清除当前图形
            plt.clf()
            plt.close()
            raise


# 创建全局实例供直接使用
heatmap = HeatMap()

def generate_heatmap(*args, **kwargs):
    """热力图生成函数，直接调用HeatMap类的generate方法"""
    return heatmap.generate(*args, **kwargs)