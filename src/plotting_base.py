#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import os
import logging
# 导入字体工具
from src.utils.font_utils import set_matplotlib_fonts

# 获取logger实例
logger = logging.getLogger(__name__)


class PlottingBase:
    """绘图基类，提供通用的绘图功能和工具方法"""
    
    def __init__(self):
        # 初始化时设置字体
        self._setup_fonts()
        # 存储主题配置
        self.themes = {
            'default': {
                'axes.facecolor': 'white',
                'axes.edgecolor': '#000000',
                'text.color': '#000000',
                'axes.labelcolor': '#000000',
                'xtick.color': '#000000',
                'ytick.color': '#000000',
                'grid.color': '#cccccc',
            }
        }
        # 缓存字体信息
        self._font_cache = None
    
    def _setup_fonts(self):
        """设置matplotlib中文字体和全局样式"""
        # 使用font_utils中的字体设置函数
        success = set_matplotlib_fonts()
        if success:
            # 设置额外的全局样式参数
            plt.rcParams["axes.labelweight"] = "bold"   # 坐标轴标签加粗
            plt.rcParams["axes.titleweight"] = "bold"   # 标题加粗
            plt.rcParams["axes.grid"] = True           # 默认显示网格
            plt.rcParams["grid.alpha"] = 0.3           # 网格透明度
            plt.rcParams["grid.linestyle"] = "--"       # 网格线型
            plt.rcParams["figure.facecolor"] = "white"  # 图形背景色
            plt.rcParams["figure.figsize"] = (10, 6)   # 默认图形大小
        else:
            logger.warning("字体设置失败，使用matplotlib默认配置")
    
    def _set_theme(self, theme_name: str):
        """设置图表主题
        
        Args:
            theme_name: 主题名称
        """
        if theme_name in self.themes:
            for key, value in self.themes[theme_name].items():
                plt.rcParams[key] = value
        elif hasattr(plt.style, 'use') and theme_name in plt.style.available:
            # 如果是matplotlib内置主题
            plt.style.use(theme_name)
    
    def _validate_path(self, file_path: str) -> bool:
        """验证文件路径是否合法
        
        Args:
            file_path: 要验证的文件路径
            
        Returns:
            bool: 路径是否合法
        """
        if not file_path:
            return False
            
        # 检查是否包含非法字符
        invalid_chars = set('<>"|?*')
        if any(char in invalid_chars for char in file_path):
            return False
            
        # 检查路径长度（不同系统有不同限制，这里设置一个合理的值）
        if len(file_path) > 4096:
            return False
            
        return True
        
    def _save_plot(self, save_path: str = None, plot_type: str = "plot") -> str:
        """保存图表并返回文件路径
        
        Args:
            save_path: 保存路径
            plot_type: 图表类型
            
        Returns:
            str: 保存的文件绝对路径
            
        Raises:
            ValueError: 保存失败时抛出
        """
        # 保存到文件
        file_path = save_path if save_path else f"{plot_type}_output.png"
            
        # 路径校验
        try:
            # 检查路径是否合法
            if not self._validate_path(file_path):
                raise ValueError(f"无效的文件路径: {file_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            plt.savefig(file_path, dpi=100, bbox_inches="tight")
            
            # 清除当前图形
            plt.clf()
            plt.close()
            
            return os.path.abspath(file_path)
        except Exception as e:
                # 清除当前图形
                plt.clf()
                plt.close()
                raise ValueError(f"保存图表失败: {str(e)}")
