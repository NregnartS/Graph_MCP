#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import logging
from typing import List, Dict, Any, Optional
from src.plotting_base import PlottingBase

# 获取logger实例
logger = logging.getLogger(__name__)


class BarChart(PlottingBase):
    """柱状图生成器"""
    
    def __init__(self):
        super().__init__()
    
    def generate(
        self,
        data: List[Dict[str, Any]],
        x_field: str,
        y_fields: List[str],
        title: str = "柱状图",
        x_label: str = None,
        y_label: str = None,
        colors: List[str] = None,
        bar_width: float = 0.8,
        stack: bool = False,
        edge_color: str = 'black',
        edge_width: float = 0.5,
        horizontal: bool = False,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (10, 6),
        dpi: int = 100,
        grid: bool = True
    ) -> str:
        """
        生成柱状图
        
        参数:
            data: 数据列表
            x_field: X轴字段名
            y_fields: Y轴字段名列表
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            colors: 柱状图颜色列表
            bar_width: 柱子宽度
            stack: 是否堆叠显示
            edge_color: 柱子边框颜色
            edge_width: 柱子边框宽度
            horizontal: 是否水平显示
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
            
            # 使用seaborn的barplot
            if len(y_fields) == 1:
                # 单个y字段的情况
                y_field = y_fields[0]
                ax = sns.barplot(
                    data=df,
                    x=x_field if not horizontal else y_field,
                    y=y_field if not horizontal else x_field,
                    color=colors[0] if colors and len(colors) > 0 else None,
                    palette=colors if colors else None,
                    width=bar_width,
                    ax=plt.gca()
                )
            else:
                # 多个y字段的情况
                if stack:
                    # 堆叠柱状图实现
                    ax = plt.gca()
                    x_values = df[x_field].unique()
                    x_pos = np.arange(len(x_values))
                    bottom = np.zeros(len(x_values))
                    
                    for i, y_field in enumerate(y_fields):
                        color = colors[i] if colors and i < len(colors) else None
                        bars = ax.bar(x_pos if not horizontal else df[y_field],
                                      df[y_field] if not horizontal else x_pos,
                                      bar_width,
                                      bottom=bottom if not horizontal else None,
                                      left=bottom if horizontal else None,
                                      label=y_field,
                                      color=color)
                        
                        # 添加边框
                        for patch in bars:
                            patch.set_edgecolor(edge_color)
                            patch.set_linewidth(edge_width)
                        
                        # 更新堆叠位置
                        bottom += df[y_field].to_numpy()
                    
                    # 设置x轴标签
                    if not horizontal:
                        ax.set_xticks(x_pos)
                        ax.set_xticklabels(x_values)
                    else:
                        ax.set_yticks(x_pos)
                        ax.set_yticklabels(x_values)
                else:
                    # 分组柱状图实现（使用长格式数据）
                    long_df = pd.melt(df, id_vars=[x_field], value_vars=y_fields, 
                                     var_name='Series', value_name='Value')
                    
                    ax = sns.barplot(
                        data=long_df,
                        x=x_field if not horizontal else 'Value',
                        y='Value' if not horizontal else x_field,
                        hue='Series',
                        palette=colors if colors else None,
                        width=bar_width,
                        ax=plt.gca()
                    )
            
            # 设置边框
            for patch in ax.patches:
                patch.set_edgecolor(edge_color)
                patch.set_linewidth(edge_width)
            
            # 设置标题和标签
            ax.set_title(title, fontsize=16)
            if horizontal:
                ax.set_ylabel(x_label or x_field, fontsize=12)
                if y_label:
                    ax.set_xlabel(y_label, fontsize=12)
            else:
                ax.set_xlabel(x_label or x_field, fontsize=12)
                if y_label:
                    ax.set_ylabel(y_label, fontsize=12)
            
            # 设置刻度字体大小
            ax.tick_params(axis='both', labelsize=10)
            
            # 调整x轴标签旋转
            if not horizontal:
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45 if len(df) > 5 else 0, ha='right')
            
            # 添加图例
            if len(y_fields) > 1:
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles=handles, labels=labels, fontsize=10, loc='best', framealpha=0.8)
            
            # 设置网格
            if grid:
                ax.grid(axis='y', linestyle="--", alpha=0.5)
            
            plt.tight_layout()
            
            # 保存图表
            return self._save_plot(save_path, "bar_chart")
        except Exception as e:
            logger.error(f"生成柱状图失败: {str(e)}")
            # 确保清除当前图形
            plt.clf()
            plt.close()
            raise


# 创建全局实例供直接使用
bar_chart = BarChart()

def generate_bar_chart(*args, **kwargs):
    """柱状图生成函数，直接调用BarChart类的generate方法"""
    return bar_chart.generate(*args, **kwargs)