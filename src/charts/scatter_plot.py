#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import logging
from typing import List, Dict, Any, Optional
from src.plotting_base import PlottingBase

# 获取logger实例
logger = logging.getLogger(__name__)


class ScatterPlot(PlottingBase):
    """散点图生成器"""
    
    def __init__(self):
        super().__init__()
    
    def generate(
        self,
        data: List[Dict[str, Any]],
        x_field: str,
        y_field: str,
        title: str = "散点图",
        x_label: str = None,
        y_label: str = None,
        color_field: str = None,
        size_field: str = None,
        color_map: str = 'viridis',
        marker_style: str = 'o',
        alpha: float = 0.7,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (10, 6),
        dpi: int = 100,
        grid: bool = True
    ) -> str:
        """
        生成散点图
        
        参数:
            data: 数据列表
            x_field: X轴字段名
            y_field: Y轴字段名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color_field: 颜色分组字段
            size_field: 点大小字段
            color_map: 颜色映射
            marker_style: 标记样式
            alpha: 透明度
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
            if not y_field:
                raise ValueError("Y轴字段名不能为空")
            
            df = pd.DataFrame(data)
            
            # 检查字段是否存在
            if x_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{x_field}'")
            if y_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{y_field}'")
            if color_field and color_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{color_field}'")
            if size_field and size_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{size_field}'")
            
            # 设置主题
            self._set_theme(theme)
            
            # 创建图形
            plt.figure(figsize=figsize, dpi=dpi)
            ax = plt.gca()
            
            # 准备散点图参数
            scatter_kwargs = {
                'x': df[x_field],
                'y': df[y_field],
                'marker': marker_style,
                'alpha': alpha,
                'cmap': color_map
            }
            
            # 如果指定了颜色字段和大小字段
            if color_field and size_field:
                # 检查颜色字段是否为分类类型，如果是则转换为数值编码
                if pd.api.types.is_object_dtype(df[color_field]):
                    # 将分类值映射到数值
                    category_map = {cat: i for i, cat in enumerate(df[color_field].unique())}
                    scatter_kwargs['c'] = df[color_field].map(category_map)
                else:
                    scatter_kwargs['c'] = df[color_field]
                scatter_kwargs['s'] = df[size_field]
                sc = ax.scatter(**scatter_kwargs)
                
                # 添加颜色图例
                cbar = plt.colorbar(sc, ax=ax)
                cbar.set_label(color_field, fontsize=12)
                
                # 添加大小图例（自定义实现）
                # 找到大小的最小、最大和中间值
                min_size = df[size_field].min()
                max_size = df[size_field].max()
                mid_size = (min_size + max_size) / 2
                
                # 创建自定义图例
                from matplotlib.lines import Line2D
                legend_elements = [
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=min_size/20, label=f'{size_field}: {min_size}'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=mid_size/20, label=f'{size_field}: {mid_size:.1f}'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=max_size/20, label=f'{size_field}: {max_size}')
                ]
                ax.legend(handles=legend_elements, title='Size', loc='best', framealpha=0.8)
            elif color_field:
                # 检查颜色字段是否为分类类型，如果是则转换为数值编码
                if pd.api.types.is_object_dtype(df[color_field]):
                    # 将分类值映射到数值
                    category_map = {cat: i for i, cat in enumerate(df[color_field].unique())}
                    scatter_kwargs['c'] = df[color_field].map(category_map)
                else:
                    scatter_kwargs['c'] = df[color_field]
                sc = ax.scatter(**scatter_kwargs)
                
                # 添加颜色图例
                cbar = plt.colorbar(sc, ax=ax)
                cbar.set_label(color_field, fontsize=12)
            elif size_field:
                scatter_kwargs['s'] = df[size_field]
                ax.scatter(**scatter_kwargs)
                
                # 添加大小图例
                min_size = df[size_field].min()
                max_size = df[size_field].max()
                mid_size = (min_size + max_size) / 2
                
                from matplotlib.lines import Line2D
                legend_elements = [
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=min_size/20, label=f'{size_field}: {min_size}'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=mid_size/20, label=f'{size_field}: {mid_size:.1f}'),
                    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=max_size/20, label=f'{size_field}: {max_size}')
                ]
                ax.legend(handles=legend_elements, title='Size', loc='best', framealpha=0.8)
            else:
                # 基本散点图
                ax.scatter(**scatter_kwargs)
            
            # 设置标题和标签
            ax.set_title(title, fontsize=16)
            ax.set_xlabel(x_label or x_field, fontsize=12)
            ax.set_ylabel(y_label or y_field, fontsize=12)
            
            # 设置刻度字体大小
            ax.tick_params(axis='both', labelsize=10)
            
            # 设置网格
            if grid:
                ax.grid(True, linestyle="--", alpha=0.5)
            
            plt.tight_layout()
            
            # 保存图表
            return self._save_plot(save_path, "scatter_plot")
        except Exception as e:
            logger.error(f"生成散点图失败: {str(e)}")
            # 确保清除当前图形
            plt.clf()
            plt.close()
            raise


# 创建全局实例供直接使用
scatter_plot = ScatterPlot()

def generate_scatter_plot(*args, **kwargs):
    """散点图生成函数，直接调用ScatterPlot类的generate方法"""
    return scatter_plot.generate(*args, **kwargs)