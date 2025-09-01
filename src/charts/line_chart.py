#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from src.plotting_base import PlottingBase

# 获取logger实例
logger = logging.getLogger(__name__)


class LineChart(PlottingBase):
    """折线图生成器"""
    
    def __init__(self):
        super().__init__()
    
    def generate(
        self,
        data: List[Dict[str, Any]],
        x_field: str,
        y_fields: List[str],
        title: str = "折线图",
        x_label: str = None,
        y_label: str = None,
        colors: List[str] = None,
        line_styles: List[str] = None,
        line_widths: List[float] = None,
        markers: List[str] = None,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (10, 6),
        dpi: int = 100,
        grid: bool = True
    ) -> str:
        """
        生成折线图
        
        参数:
            data: 数据列表，每个元素是包含字段和值的字典
            x_field: X轴字段名
            y_fields: Y轴字段名列表（可绘制多条线）
            title: 图表标题
            x_label: X轴标签，如果为None则使用x_field
            y_label: Y轴标签
            colors: 线条颜色列表
            line_styles: 线条样式列表，有效值为['-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted']
            line_widths: 线条宽度列表
            markers: 标记样式列表
            theme: 图表主题
            save_path: 保存路径
            figsize: 图形大小
            dpi: 图像分辨率
            grid: 是否显示网格
        
        返回:
            文件路径
        """
        try:
            # 验证必要参数
            if not data:
                raise ValueError("数据不能为空")
            if not x_field:
                raise ValueError("X轴字段名不能为空")
            if not y_fields:
                raise ValueError("Y轴字段名列表不能为空")
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(data)
            
            # 检查字段是否存在
            if x_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{x_field}'")
            for y_field in y_fields:
                if y_field not in df.columns:
                    raise ValueError(f"数据中不存在字段 '{y_field}'")
            
            # 设置主题
            self._set_theme(theme)
            
            # 创建图形
            plt.figure(figsize=figsize, dpi=dpi)
            ax = plt.gca()
            
            # 准备默认值
            if line_styles is None:
                line_styles = ['-'] * len(y_fields)
            if line_widths is None:
                line_widths = [1.5] * len(y_fields)
            if markers is None:
                markers = ['o'] * len(y_fields)
            
            # 为每条线应用不同的样式
            for i, y_field in enumerate(y_fields):
                # 获取当前线条的样式参数
                color = colors[i] if colors and i < len(colors) else None
                line_style = line_styles[i] if i < len(line_styles) else line_styles[0]
                line_width = line_widths[i] if i < len(line_widths) else line_widths[0]
                marker = markers[i] if i < len(markers) else markers[0]
                
                # 使用matplotlib的plot函数绘制线条，支持不同样式
                ax.plot(
                    df[x_field],
                    df[y_field],
                    label=y_field,
                    color=color,
                    linestyle=line_style,
                    linewidth=line_width,
                    marker=marker,
                    markersize=6
                )
            
            # 设置标题和标签
            ax.set_title(title, fontsize=16)
            ax.set_xlabel(x_label or x_field, fontsize=12)
            if y_label:
                ax.set_ylabel(y_label, fontsize=12)
            
            # 设置刻度字体大小
            ax.tick_params(axis='both', labelsize=10)
            
            # 设置网格
            if grid:
                ax.grid(True, linestyle="--", alpha=0.5)
            
            # 调整图例
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles=handles, labels=labels, fontsize=10, loc='best', framealpha=0.8)
            
            plt.tight_layout()
            
            # 保存图表
            return self._save_plot(save_path, "line_chart")
        except Exception as e:
            logger.error(f"生成折线图失败: {str(e)}")
            # 确保清除当前图形
            plt.clf()
            plt.close()
            raise


# 创建全局实例供直接使用
line_chart = LineChart()

def generate_line_chart(*args, **kwargs):
    """折线图生成函数，直接调用LineChart类的generate方法"""
    return line_chart.generate(*args, **kwargs)