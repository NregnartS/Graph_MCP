#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mcp.server.fastmcp import FastMCP
import threading
import argparse
import logging
# 导入日志配置
from src.utils.logging_config import logger
# 导入图表生成函数
from src.charts.line_chart import generate_line_chart
from src.charts.bar_chart import generate_bar_chart
from src.charts.pie_chart import generate_pie_chart
from src.charts.scatter_plot import generate_scatter_plot
from src.charts.heatmap import generate_heatmap
from src.charts.mermaid_chart import generate_mermaid_chart

# 导入工具函数
from src.utils.plotting_utils import (
    ChartConfig,
    process_nested_params,
    validate_parameters,
    get_target_function,
    filter_kwargs,
    check_required_params,
    execute_plotting,
    handle_plotting_exception
)

# 导入字体工具
from src.utils.font_utils import setup_fonts

# 解析命令行参数
parser = argparse.ArgumentParser(description='MCP绘图服务')
parser.add_argument('--port', type=int, default=16666, help='服务端口号，默认为16666')
parser.add_argument('--debug', action='store_true', help='启用调试模式')
args = parser.parse_args()

# 如果启用调试模式，设置应用日志为DEBUG级别
if args.debug:
    logger.setLevel(logging.DEBUG)
    logger.debug("调试模式已启用")
    # 调试模式下控制台也输出DEBUG级别日志
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(logging.DEBUG)

# 创建FastMCP服务器实例
mcp = FastMCP(name="PlottingService", host="0.0.0.0", port=args.port)


# 初始化字体设置
try:
    setup_fonts()
    logger.info("字体设置已完成")
except Exception as e:
    logger.error(f"字体设置失败: {str(e)}")

# 为ChartConfig添加图表函数映射
ChartConfig.functions = {
    'line_chart': generate_line_chart,
    'bar_chart': generate_bar_chart,
    'pie_chart': generate_pie_chart,
    'scatter_plot': generate_scatter_plot,
    'heatmap': generate_heatmap,
    'mermaid_chart': generate_mermaid_chart
}

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
            - theme: 图表主题（默认: "default"，Mermaid支持'default', 'dark', 'forest', 'neutral'。其余图表则支持所有Matplotlib内置主题）
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
                legend: 是否显示图例（默认: True）
                legend_loc: 图例位置（默认: 'right'）
                
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
                width: 图像宽度（默认: 800）
                height: 图像高度（默认: 600）
        
    Returns:
        dict: 包含图表保存路径和状态的响应
    """
    try:
        # logger.info(f"接收到的参数: plot_type={plot_type}, params={params}")
        
        # 处理嵌套参数结构
        params = process_nested_params(params)
        # logger.debug(f"处理后的参数: {params}")
        
        # 检查图表类型支持
        if plot_type not in ChartConfig.functions:
            raise ValueError(f"不支持的图表类型: {plot_type}")
        
        # 验证参数
        validate_parameters(plot_type, params)
        
        # 获取绘图函数和过滤参数
        plot_func = ChartConfig.functions[plot_type]
        target_func, target_sig = get_target_function(plot_type, plot_func)
        filtered_params = filter_kwargs(params, target_sig)
        
        # 检查必需参数
        check_required_params(plot_type, params)
        
        # 执行绘图
        logger.info(f"生成图表，图表类型: {plot_type}")
        result = execute_plotting(plot_func, filtered_params, target_sig)
        
        return {"status": "success", "message": "图表生成成功", "save_path": result}
    except Exception as e:
        return handle_plotting_exception(e, args.debug)


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