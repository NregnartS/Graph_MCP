# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.font_manager as fm
import seaborn as sns
import matplotlib.pyplot as plt
from mermaid import Mermaid
import subprocess
import logging

# 获取logger实例
logger = logging.getLogger(__name__)


# 设置matplotlib中文字体和全局样式
def setup_matplotlib_fonts():
    # 查找并设置系统中可用的中文字体
    chinese_fonts = []
    for font_path in fm.findSystemFonts():
        try:
            font_filename = os.path.basename(font_path)
            if any(keyword in font_filename.lower() for keyword in ['wqy', 'uming', 'hei', 'song']):
                font_name = fm.FontProperties(fname=font_path).get_name()
                chinese_fonts.append((font_name, font_path))
        except:
            pass
    
    # 优先使用找到的具体中文字体
    if chinese_fonts:
        first_font_name, _ = chinese_fonts[0]
        plt.rcParams["font.family"] = [first_font_name]
        plt.rcParams["font.sans-serif"] = [first_font_name]
        logger.info(f"已设置matplotlib字体为: {first_font_name}")
    else:
        # 如果找不到具体字体，使用通用设置
        plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Heiti TC", "SimHei"]
        plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Heiti TC", "SimHei"]
        logger.info("已设置matplotlib使用默认中文字体族")
    
    # 设置全局样式参数
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    plt.rcParams["axes.labelweight"] = "bold"   # 坐标轴标签加粗
    plt.rcParams["axes.titleweight"] = "bold"   # 标题加粗
    plt.rcParams["axes.grid"] = True           # 默认显示网格
    plt.rcParams["grid.alpha"] = 0.3           # 网格透明度
    plt.rcParams["grid.linestyle"] = "--"       # 网格线型
    plt.rcParams["figure.facecolor"] = "white"  # 图形背景色
    plt.rcParams["figure.figsize"] = (10, 6)   # 默认图形大小

# 初始化时设置字体和全局样式
setup_matplotlib_fonts()
from typing import List, Dict, Any, Optional, Union

class PlottingTools:
    """绘图工具类，封装Matplotlib等库的绘图功能，提供给LLM使用"""
    
    def __init__(self):
        # 字体设置已在模块初始化时完成
        # 这里不再重复设置，避免覆盖之前的字体选择
        # 只确保负号正确显示
        plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号
        
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
            },
            'dark': {
                'axes.facecolor': '#333333',
                'axes.edgecolor': '#ffffff',
                'text.color': '#ffffff',
                'axes.labelcolor': '#ffffff',
                'xtick.color': '#aaaaaa',
                'ytick.color': '#aaaaaa',
                'grid.color': '#555555',
                'figure.facecolor': '#1e1e1e',
                'savefig.facecolor': '#1e1e1e',
            },
            'light': {
                'axes.facecolor': '#f8f9fa',
                'axes.edgecolor': '#000000',
                'text.color': '#000000',
                'axes.labelcolor': '#000000',
                'xtick.color': '#666666',
                'ytick.color': '#666666',
                'grid.color': '#e9ecef',
            }
        }
        
        # 在初始化时检查系统是否存在mmdc命令，只检查一次
        self.mmdc_available = self._check_mmdc_available()
        if self.mmdc_available:
            logger.info("mmdc命令已检测到，将使用mmdc生成mermaid图表")
        else:
            logger.info("mmdc命令不可用，将使用mermaid-py库生成mermaid图表")
            
    def _check_mmdc_available(self):
        """检查系统是否存在mmdc命令"""
        try:
            import subprocess
            # 尝试运行mmdc --version命令来检查是否安装
            subprocess.run(['mmdc', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
        
    def generate_line_chart(
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
        # 将数据转换为DataFrame
        df = pd.DataFrame(data)
        
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
        
        return self._save_plot(save_path, "line_chart")
    
    def _set_theme(self, theme_name):
        """设置图表主题"""
        if theme_name in self.themes:
            for key, value in self.themes[theme_name].items():
                plt.rcParams[key] = value
        elif hasattr(plt.style, 'use') and theme_name in plt.style.available:
            # 如果是matplotlib内置主题
            plt.style.use(theme_name)
    
    def generate_bar_chart(
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
        生成柱状图（使用Seaborn优化）
        
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
        df = pd.DataFrame(data)
        
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
        
        return self._save_plot(save_path, "bar_chart")
    
    def generate_pie_chart(
        self,
        data: List[Dict[str, Any]],
        name_field: str,
        value_field: str,
        title: str = "饼图",
        colors: List[str] = None,
        autopct: str = "%1.1f%%",
        shadow: bool = False,
        explode: List[float] = None,
        start_angle: int = 90,
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (8, 8),
        dpi: int = 100,
        labeldistance: float = 1.1
    ) -> str:
        """
        生成饼图（使用Seaborn优化）
        
        参数:
            data: 数据列表
            name_field: 名称字段名
            value_field: 数值字段名
            title: 图表标题
            colors: 饼图颜色列表
            autopct: 百分比格式
            shadow: 是否显示阴影
            explode: 突出显示部分
            start_angle: 起始角度
            theme: 图表主题
            save_path: 保存路径
            figsize: 图形大小
            dpi: 图像分辨率
            labeldistance: 标签距离
        
        返回:
            文件路径
        """
        df = pd.DataFrame(data)
        
        # 设置主题
        self._set_theme(theme)
        
        # 创建图形
        plt.figure(figsize=figsize, dpi=dpi)
        
        # 设置默认的explode值
        if explode is None:
            explode = [0] * len(df)
        
        # 使用seaborn的颜色主题，如果没有指定颜色
        if not colors:
            # 获取当前seaborn主题的颜色
            sns_palette = sns.color_palette()
            # 如果数据点超过palette的颜色数量，循环使用
            colors = [sns_palette[i % len(sns_palette)] for i in range(len(df))]
        
        # 绘制饼图
        wedges, texts, autotexts = plt.pie(
            df[value_field], 
            labels=df[name_field], 
            autopct=autopct,
            colors=colors,
            shadow=shadow,
            startangle=start_angle,
            explode=explode,
            labeldistance=labeldistance,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1},
            textprops={'fontsize': 12}
        )
        
        # 设置百分比文本样式
        for autotext in autotexts:
            if theme == 'dark':
                autotext.set_color('white')
            else:
                autotext.set_color('white')  # 保持白色以便在任何背景下都清晰可见
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        # 设置标题
        plt.title(title, fontsize=16, pad=20, fontweight='bold')
        plt.axis('equal')  # 保证饼图是圆形
        
        # 添加图例（当项目较多时）
        if len(df) > 6:
            plt.legend(wedges, df[name_field], title=name_field, 
                      loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                      frameon=True, framealpha=0.8, fontsize=10)
        
        plt.tight_layout()
        
        return self._save_plot(save_path, "pie_chart")
    
    def generate_scatter_plot(
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
        生成散点图（使用Seaborn优化）
        
        参数:
            data: 数据列表
            x_field: X轴字段名
            y_field: Y轴字段名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color_field: 用于颜色编码的字段名
            size_field: 用于点大小编码的字段名
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
        df = pd.DataFrame(data)
        
        # 设置主题
        self._set_theme(theme)
        
        # 创建图形和轴
        plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.gca()
        
        # 准备大小参数
        size_param = df[size_field] * 100 if size_field else 100  # 放大点大小以便更好地显示
        
        # 使用seaborn的scatterplot
        scatter = sns.scatterplot(
            data=df,
            x=x_field,
            y=y_field,
            hue=color_field if color_field else None,
            size=size_field if size_field else None,
            sizes=(min(size_param), max(size_param)) if size_field else (size_param, size_param),
            style=None,
            palette=color_map if color_field else None,
            marker=marker_style,
            alpha=alpha,
            ax=ax,
            linewidth=0.5,  # 边框宽度
            edgecolor='white'  # 白色边框
        )
        
        # 设置标题和标签
        ax.set_title(title, fontsize=16)
        ax.set_xlabel(x_label or x_field, fontsize=12)
        ax.set_ylabel(y_label or y_field, fontsize=12)
        
        # 设置刻度字体大小
        ax.tick_params(axis='both', labelsize=10)
        
        # 自定义颜色图例
        if color_field:
            # 获取当前的图例
            handles, labels = ax.get_legend_handles_labels()
            # 如果同时有颜色和大小的图例，可能需要调整
            if size_field:
                # 找到颜色部分的图例并保留
                color_handles = []
                color_labels = []
                for i, (handle, label) in enumerate(zip(handles, labels)):
                    # 颜色图例的标签不包含数字
                    if not any(char.isdigit() for char in label):
                        color_handles.append(handle)
                        color_labels.append(label)
                ax.legend(handles=color_handles, labels=color_labels, title=color_field,
                          loc='best', framealpha=0.8, fontsize=10)
            else:
                ax.legend(title=color_field, loc='best', framealpha=0.8, fontsize=10)
        
        # 设置网格
        if grid:
            ax.grid(True, linestyle="--", alpha=0.5)
        
        plt.tight_layout()
        
        return self._save_plot(save_path, "scatter_plot")
    
    def generate_heatmap(
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
        theme: str = "default",
        save_path: str = None,
        figsize: tuple = (10, 8),
        dpi: int = 100,
        linewidths: float = 0.5,
        linecolor: str = 'white',
        aggregation: str = 'mean',
        cbar_kws: dict = None
    ) -> str:
        """
        生成热力图（使用Seaborn优化）
        
        参数:
            data: 数据列表
            x_field: X轴字段名
            y_field: Y轴字段名
            value_field: 值字段名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color_map: 颜色映射
            annotate: 是否显示数值
            fmt: 数值格式
            theme: 图表主题
            save_path: 保存路径
            figsize: 图形大小
            dpi: 图像分辨率
            linewidths: 网格线宽度
            linecolor: 网格线颜色
            aggregation: 聚合函数（mean, sum, count等）
            cbar_kws: 颜色条的额外参数
        
        返回:
            文件路径
        """
        df = pd.DataFrame(data)
        
        # 检查字段是否存在
        if x_field not in df.columns:
            raise ValueError(f"数据中不存在字段 '{x_field}'，请检查 x_field 参数")
        if y_field not in df.columns:
            raise ValueError(f"数据中不存在字段 '{y_field}'，请检查 y_field 参数")
        if value_field not in df.columns:
            raise ValueError(f"数据中不存在字段 '{value_field}'，请检查 value_field 参数")
        
        # 创建透视表
        pivot_table = df.pivot_table(
            index=y_field,
            columns=x_field,
            values=value_field,
            aggfunc=aggregation
        )
        
        # 设置主题
        self._set_theme(theme)
        
        # 创建图形
        plt.figure(figsize=figsize, dpi=dpi)
        
        # 准备颜色条参数
        if cbar_kws is None:
            cbar_kws = {'label': value_field}
        else:
            # 确保有标签
            if 'label' not in cbar_kws:
                cbar_kws['label'] = value_field
        
        # 使用seaborn创建热力图
        ax = sns.heatmap(
            pivot_table,
            cmap=color_map,
            annot=annotate,
            fmt=fmt,
            linewidths=linewidths,
            linecolor=linecolor,
            cbar=True,
            square=False,
            robust=True,  # 使颜色映射更适应数据分布
            cbar_kws=cbar_kws,
            ax=plt.gca()
        )
        
        # 设置标题和标签
        ax.set_title(title, fontsize=16, pad=20, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label, fontsize=12, labelpad=10)
        else:
            ax.set_xlabel(x_field, fontsize=12, labelpad=10)
        
        if y_label:
            ax.set_ylabel(y_label, fontsize=12, labelpad=10)
        else:
            ax.set_ylabel(y_field, fontsize=12, labelpad=10)
        
        # 调整刻度标签
        ax.tick_params(axis='both', labelsize=10)
        
        # 旋转x轴标签以避免重叠
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(rotation=0, fontsize=10)
        
        # 美化注释文本样式
        if annotate:
            # 获取热力图的矩形单元格
            rectangles = [patch for patch in ax.patches if isinstance(patch, plt.Rectangle)]
            
            # 遍历文本和对应的矩形单元格
            for i, text in enumerate(ax.texts):
                text.set_size(10)
                
                # 确保索引有效
                if i < len(rectangles):
                    # 获取单元格背景颜色
                    bg_color = rectangles[i].get_facecolor()
                    
                    # 计算颜色亮度 (0-1，0为黑色，1为白色)
                    # 公式: 0.299*R + 0.587*G + 0.114*B
                    if len(bg_color) >= 3:
                        # 处理RGB或RGBA颜色
                        brightness = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
                        
                        # 根据亮度设置文本颜色
                        # 如果背景较暗，使用白色文本；如果背景较亮，使用黑色文本
                        text_color = 'white' if brightness < 0.5 else 'black'
                        text.set_color(text_color)
        
        plt.tight_layout()
        
        return self._save_plot(save_path, "heatmap")
    
    def generate_mermaid_chart(
        self,
        mermaid_code: str,
        save_path: str = None
    ) -> str:
        """
        生成Mermaid图表并保存为图片或代码文件
        
        参数:
            mermaid_code: Mermaid图表代码
            save_path: 保存路径，支持png、svg、mmd格式
        
        返回:
            文件路径
        """
        # 默认保存路径和格式
        if save_path is None:
            save_path = "mermaid_chart.mmd"
        
        # 路径校验
        try:
            # 检查路径是否合法
            if not self._validate_path(save_path):
                raise ValueError(f"无效的文件路径: {save_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            # 获取文件扩展名
            file_ext = os.path.splitext(save_path)[1].lower()
            
            # 如果明确要求保存为mmd代码文件，或没有提供扩展名，直接保存代码
            if file_ext == '.mmd' or not file_ext:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)
                return os.path.abspath(save_path)
            
            # 使用类初始化时检查的结果来决定使用哪种方式
            if self.mmdc_available:
                # 创建唯一的临时mmd文件，避免多客户端并发调用时的冲突
                import uuid
                temp_dir = os.path.dirname(os.path.abspath(save_path))
                unique_id = uuid.uuid4().hex[:8]  # 生成8位唯一ID
                temp_mmd_path = os.path.join(temp_dir, f'temp_chart_{unique_id}.mmd')
                try:
                    with open(temp_mmd_path, 'w', encoding='utf-8') as f:
                        f.write(mermaid_code)
                    
                    # 执行mmdc命令并捕获可能的异常
                    try:
                        result = subprocess.run(
                            ['mmdc', '-i', temp_mmd_path, '-o', save_path],
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    except subprocess.CalledProcessError as e:
                        # 获取详细的错误信息
                        error_msg = f"返回码: {e.returncode}\n" \
                                  f"标准错误: {e.stderr}\n" 
                        # 抛出包含详细错误信息的异常
                        raise ValueError(f"使用mmdc生成Mermaid图表失败: {error_msg}") from e
                    
                    return os.path.abspath(save_path)
                finally:
                    # 确保删除临时文件
                    try:
                        if os.path.exists(temp_mmd_path):
                            os.remove(temp_mmd_path)
                    except Exception as cleanup_error:
                        # 记录清理失败但不阻止主流程
                        import logging
                        logging.warning(f"清理临时文件失败: {str(cleanup_error)}")
            else:
                # 如果mmdc命令不可用，使用mermaid-py作为替代方案
                mermaid = Mermaid(mermaid_code)
                if file_ext == '.png':
                    mermaid.to_png(save_path)
                elif file_ext == '.svg':
                    mermaid.to_svg(save_path)
                return os.path.abspath(save_path)
        except Exception as e:
            raise ValueError(f"生成Mermaid图表失败: {str(e)}")

    def _validate_path(self, file_path: str) -> bool:
        """验证文件路径是否合法"""
        if not file_path:
            return False
            
        # 检查是否包含非法字符
        invalid_chars = set('<>"|?*')
        if any(char in invalid_chars for char in file_path):
            return False
            
        # 检查路径长度（不同系统有不同限制，这里设置一个合理的值）
        if len(file_path) > 4096:
            return False
            
        # 检查是否是绝对路径
        # 注意：这里不强制要求是绝对路径，因为用户可能提供相对路径
        # 如果需要强制绝对路径，可以取消下面的注释
        # if not os.path.isabs(file_path):
        #     return False
            
        return True
        
    def _save_plot(self, save_path: str = None, plot_type: str = "plot") -> str:
        """保存图表并返回文件路径"""
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