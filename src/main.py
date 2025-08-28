#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from crypt import methods
from operator import methodcaller
from mcp.server.fastmcp import FastMCP
import threading
import inspect
from plotting_tools import PlottingTools
from plot_params import validate_and_convert_params
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP(name="PlottingService",host="0.0.0.0",port=16666)

# 创建绘图工具实例
drawing_tools = PlottingTools()

@mcp.tool()
def create_plotting_task(plot_type, **params):
    """
    生成图表并保存到指定路径
    
    Args:
        plot_type: 图表类型，可选'line_chart', 'bar_chart', 'pie_chart', 'scatter_plot', 'heatmap', 'mermaid_chart'
        **params: 所有图表参数，根据图表类型不同所需参数不同。使用pydantic库解析
            
        基础通用参数支持情况:
            - save_path: 保存路径（必需，绝对路径），除Mermaid图外支持png、svg、jpg、jpeg、pdf等格式,Mermaid图支持png、svg、mmd格式
            - data: 数据列表（必需，支持除Mermaid图外的所有图表类型），示例: [{"x": 1, "y": 2}, {"x": 2, "y": 3}]
            - title: 图表标题（默认值: "图表标题"，支持除Mermaid图外的所有图表类型）
            - figsize: 图表尺寸，如 (10, 6)（默认: (10, 6)，支持除Mermaid图外的所有图表类型，饼图默认(8,8)）
            - dpi: 分辨率（默认: 100，支持除Mermaid图外的所有图表类型）
            - theme: 支持所有matplotlib内置主题（默认: "default"，支持除Mermaid图外的所有图表类型），可选值包括: 'default', 'classic', 'dark_background', 'seaborn', 'ggplot'
            - colors: 颜色列表（可选，用于折线图、柱状图和饼图），示例: ['#1f77b4', '#ff7f0e', '#2ca02c']
            - grid: 是否显示网格（默认: True，用于折线图、柱状图和散点图）
            
        各图表类型特定参数:
            line_chart（折线图）:
                x_field: X轴字段名（必需）
                y_fields: Y轴字段名列表（必需，支持绘制多条线），可以是字符串数组或逗号分隔的字符串
                x_label: X轴标签（可选，默认使用x_field值）
                y_label: Y轴标签（可选）
                line_styles: 线条样式列表（可选），有效值为: ['-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted']
                markers: 标记样式列表（可选），示例值: ['o', 's', '^', 'D', 'x', '*', '+']
                line_widths: 线条宽度列表（默认: [1.5]），示例值: [1.5, 2.0, 3.0]
                
            bar_chart（柱状图）:
                x_field: X轴字段名（必需）
                y_fields: Y轴字段名列表（必需，支持多个数据系列），可以是字符串数组或逗号分隔的字符串
                x_label: X轴标签（可选，默认使用x_field值）
                y_label: Y轴标签（可选）
                bar_width: 柱状宽度（默认: 0.8），范围: 0-1
                stack: 是否堆叠显示（默认: False）
                edge_color: 边框颜色（默认: 'black'），支持颜色名称或十六进制值
                edge_width: 边框宽度（默认: 0.5）
                horizontal: 是否水平显示（默认: False）
                
            pie_chart（饼图）:
                name_field: 名称字段（必需）
                value_field: 数值字段（必需）
                explode: 突出显示的扇区列表（可选，默认全0），示例: [0, 0.1, 0]（第二个扇区突出）
                autopct: 百分比格式，如 "%1.1f%%"（默认: "%1.1f%%"），控制百分比显示格式
                start_angle: 起始角度（默认: 90），控制饼图的起始角度
                shadow: 是否显示阴影（默认: False）
                labeldistance: 标签距离（默认: 1.1），控制标签与中心的距离
                
            scatter_plot（散点图）:
                x_field: X轴字段名（必需）
                y_field: 单个Y轴字段名（必需，注意与line_chart和bar_chart的y_fields区分）
                x_label: X轴标签（可选，默认使用x_field值）
                y_label: Y轴标签（可选，默认使用y_field值）
                color_field: 颜色分组字段（可选）
                size_field: 点大小字段（可选）
                color_map: 颜色映射（默认: 'viridis'），可选值参考matplotlib的colormap，如 'plasma', 'inferno', 'magma', 'cividis'
                marker_style: 标记样式（默认: 'o'），示例值: 'o', 's', '^', 'D', 'x', '*', '+'
                alpha: 透明度（默认: 0.7），范围: 0-1
                
            heatmap（热力图）:
                x_field: X轴字段名（必需）
                y_field: Y轴字段名（必需）
                value_field: 数值字段（必需）
                x_label: X轴标签（可选，默认使用x_field值）
                y_label: Y轴标签（可选，默认使用y_field值）
                color_map: 颜色映射（默认: 'viridis'），可选值参考matplotlib的colormap
                annotate: 是否显示数值（默认: True）
                fmt: 数值格式（默认: '.2f'），控制数值显示格式
                linewidths: 网格线宽度（默认: 0.5）
                linecolor: 网格线颜色（默认: 'white'）
                aggregation: 聚合函数（默认: 'mean'），可选值: 'mean', 'sum', 'max', 'min', 'count'
                cbar_kws: 颜色条参数（可选），字典格式，用于自定义颜色条
                
            mermaid_chart（Mermaid图）:
                mermaid_code: Mermaid图代码（必需）
                # Mermaid图仅支持save_path基础参数，不支持其他通用参数
        
    Returns:
        dict: 包含图表保存路径和状态的响应
    """
    try:
        # 处理params参数，如果params是一个包含单个'params'键的字典
        logger.info(f"接收到的参数: plot_type={plot_type}, params={params}")
        
        # 检查是否是嵌套的params结构
        if isinstance(params, dict) and 'params' in params and len(params) == 1:
            logger.info("检测到嵌套的params结构，提取内部参数")
            params = params['params']
        
        # 使用pydantic模型验证并转换参数
        validated_params = validate_and_convert_params(plot_type, params)
        
        # 确保save_path参数存在
        save_path = validated_params.get('save_path')
        if not save_path:
            raise ValueError("缺少必需的参数: save_path")
        
        logger.info(f"生成图表，图表类型: {plot_type}")
        
        # 直接调用绘图工具的相应函数
        # 过滤掉绘图函数不接受的参数
        if plot_type == 'line_chart':
            # 获取generate_line_chart函数接受的参数列表
            sig = inspect.signature(drawing_tools.generate_line_chart)
            # 只传递函数接受的参数
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_line_chart(**filtered_params)
        elif plot_type == 'bar_chart':
            # 类似处理
            sig = inspect.signature(drawing_tools.generate_bar_chart)
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_bar_chart(**filtered_params)
        elif plot_type == 'pie_chart':
            # 类似处理
            sig = inspect.signature(drawing_tools.generate_pie_chart)
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_pie_chart(**filtered_params)
        elif plot_type == 'scatter_plot':
            # 类似处理
            sig = inspect.signature(drawing_tools.generate_scatter_plot)
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_scatter_plot(**filtered_params)
        elif plot_type == 'heatmap':
            # 类似处理
            sig = inspect.signature(drawing_tools.generate_heatmap)
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_heatmap(**filtered_params)
        elif plot_type == 'mermaid_chart':
            # 类似处理
            sig = inspect.signature(drawing_tools.generate_mermaid_chart)
            filtered_params = {k: v for k, v in validated_params.items() if k in sig.parameters}
            result = drawing_tools.generate_mermaid_chart(**filtered_params)
        else:
            raise ValueError(f"不支持的图表类型: {plot_type}")
        
        return {"status": "success", "message": "图表生成成功", "save_path": result}
    except Exception as e:
        logger.exception("生成图表时发生异常")
        return {"status": "error", "message": f"生成图表失败: {str(e)}"}


# 启动MCP服务线程
def run_mcp_service():
    logger.info('启动MCP绘图服务...')
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f'MCP服务启动失败: {str(e)}')

if __name__ == "__main__":
    # 在主线程中启动服务
    mcp_thread = threading.Thread(target=run_mcp_service, daemon=True)
    mcp_thread.start()
    
    # 保持主线程运行
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        logger.info("MCP绘图服务已停止")