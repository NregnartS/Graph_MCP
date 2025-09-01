#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from src.plotting_base import PlottingBase

# 获取logger实例
logger = logging.getLogger(__name__)


class PieChart(PlottingBase):
    """饼图生成器"""
    
    def __init__(self):
        super().__init__()
    
    def generate(
        self,
        data: List[Dict[str, Any]],
        name_field: str,
        value_field: str,
        title: str = "饼图",
        explode: List[float] = None,
        autopct: str = "%1.1f%%",
        start_angle: float = 90,
        shadow: bool = False,
        labeldistance: float = 1.1,
        colors: List[str] = None,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (8, 8),
        dpi: int = 100,
        legend: bool = True,
        legend_loc: str = 'right'
    ) -> str:
        """
        生成饼图
        
        参数:
            data: 数据列表
            name_field: 名称字段
            value_field: 数值字段
            title: 图表标题
            explode: 突出显示的扇区列表，示例: [0, 0.1, 0]（第二个扇区突出）
            autopct: 百分比格式，如 "%1.1f%%"
            start_angle: 起始角度
            shadow: 是否显示阴影
            labeldistance: 标签距离
            colors: 颜色列表
            theme: 图表主题
            save_path: 保存路径
            figsize: 图形大小，默认(8,8)更适合饼图
            dpi: 图像分辨率
            legend: 是否显示图例
            legend_loc: 图例位置
        
        返回:
            文件路径
        """
        try:
            # 验证必要参数
            if not data:
                raise ValueError("数据不能为空")
            if not name_field:
                raise ValueError("名称字段名不能为空")
            if not value_field:
                raise ValueError("数值字段名不能为空")
            
            df = pd.DataFrame(data)
            
            # 检查字段是否存在
            if name_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{name_field}'")
            if value_field not in df.columns:
                raise ValueError(f"数据中不存在字段 '{value_field}'")
            
            # 检查数值是否都是非负数
            if (df[value_field] < 0).any():
                raise ValueError("饼图数据不能包含负值")
            
            # 检查数值是否都为零
            if (df[value_field] == 0).all():
                raise ValueError("饼图数据不能全部为零")
            
            # 设置主题
            self._set_theme(theme)
            
            # 创建图形
            plt.figure(figsize=figsize, dpi=dpi)
            ax = plt.gca()
            
            # 准备数据
            labels = df[name_field].tolist()
            sizes = df[value_field].tolist()
            
            # 设置默认值
            if explode is None:
                explode = [0] * len(sizes)
            else:
                # 确保explode长度与数据长度一致
                if len(explode) != len(sizes):
                    raise ValueError(f"explode参数长度({len(explode)})与数据长度({len(sizes)})不匹配")
            
            # 使用matplotlib的pie函数
            wedges, texts, autotexts = ax.pie(
                sizes,
                explode=explode,
                labels=None if not legend_loc else labels if labeldistance > 1.0 else None,
                colors=colors if colors else None,
                autopct=autopct,
                shadow=shadow,
                startangle=start_angle,
                labeldistance=labeldistance,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            
            # 设置标题
            ax.set_title(title, fontsize=16)
            
            # 设置百分比文本样式
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_weight('bold')
            
            # 设置标签样式
            for text in texts:
                text.set_fontsize(10)
            
            # 添加图例
            if legend and legend_loc:
                ax.legend(wedges, labels, title=name_field, loc=legend_loc, 
                         bbox_to_anchor=(1, 0, 0.5, 1) if legend_loc == 'right' else None, 
                         framealpha=0.8)
            
            # 确保饼图是正圆形
            ax.axis('equal')
            
            plt.tight_layout()
            
            # 保存图表
            return self._save_plot(save_path, "pie_chart")
        except Exception as e:
            logger.error(f"生成饼图失败: {str(e)}")
            # 确保清除当前图形
            plt.clf()
            plt.close()
            raise


# 创建全局实例供直接使用
pie_chart = PieChart()

def generate_pie_chart(*args, **kwargs):
    """饼图生成函数，直接调用PieChart类的generate方法"""
    return pie_chart.generate(*args, **kwargs)