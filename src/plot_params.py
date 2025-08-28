from pydantic import BaseModel, Field, validator, model_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class PlotType(str, Enum):
    # 图表类型枚举
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEAT_MAP = "heatmap"
    MERMAID_CHART = "mermaid_chart"


class NoDataBasePlotParams(BaseModel):
    # 不需要数据列表的图表基础参数模型
    save_path: str = "/tmp/plot_output.png"

class BasePlotParams(NoDataBasePlotParams):
    # 所有需要数据列表的图表类型的基础参数模型
    data: List[Dict[str, Any]]
    title: str = "图表标题"
    figsize: tuple = (10, 6)
    dpi: int = 100
    theme: str = "default"

class ColorablePlotParams(BasePlotParams):
    # 支持自定义颜色的图表参数模型（适用于折线图、柱状图和饼图）
    colors: Optional[List[str]] = None

class GridablePlotParams(BasePlotParams):
    # 支持显示网格的图表参数模型（适用于折线图、柱状图和散点图）
    grid: bool = True





class LineChartParams(ColorablePlotParams, GridablePlotParams):
    # 折线图参数模型
    x_field: str
    y_fields: List[str]  # 支持多个Y轴字段
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    line_styles: Optional[List[str]] = None  # 线条样式列表，有效值为['-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted']，与函数参数保持一致
    markers: Optional[List[str]] = None  # 标记样式列表，与函数参数保持一致
    line_widths: Optional[List[float]] = None  # 线条宽度列表，与函数参数保持一致

    # 处理逗号分隔的字符串转为列表
    @validator('y_fields', pre=True)
    def convert_y_fields_str_to_list(cls, v):
        if isinstance(v, str) and ',' in v:
            return [field.strip() for field in v.split(',')]
        return v

    # 自动设置标签如果未提供
    @model_validator(mode='after')
    def set_labels(self):
        if self.x_label is None and hasattr(self, 'x_field'):
            self.x_label = self.x_field
        if self.y_label is None and hasattr(self, 'y_fields') and len(self.y_fields) == 1:
            self.y_label = self.y_fields[0]
        return self


class BarChartParams(ColorablePlotParams, GridablePlotParams):
    # 柱状图参数模型
    x_field: str
    y_fields: List[str]  # 支持多个Y轴字段
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    bar_width: float = 0.8  # 柱状宽度
    stack: bool = False  # 是否堆叠
    horizontal: bool = False  # 是否水平显示
    edge_color: str = 'black'  # 柱子边框颜色
    edge_width: float = 0.5  # 柱子边框宽度

    # 处理逗号分隔的字符串转为列表
    @validator('y_fields', pre=True)
    def convert_y_fields_str_to_list(cls, v):
        if isinstance(v, str) and ',' in v:
            return [field.strip() for field in v.split(',')]
        return v

    # 自动设置标签如果未提供
    @model_validator(mode='after')
    def set_labels(self):
        if self.x_label is None and hasattr(self, 'x_field'):
            self.x_label = self.x_field
        if self.y_label is None and hasattr(self, 'y_fields') and len(self.y_fields) == 1:
            self.y_label = self.y_fields[0]
        return self


class ScatterPlotParams(GridablePlotParams):
    # 散点图参数模型
    x_field: str
    y_field: str  # 单个Y轴字段
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    color_field: Optional[str] = None  # 颜色分组字段
    size_field: Optional[str] = None  # 大小字段
    color_map: str = 'viridis'  # 颜色映射
    marker_style: str = 'o'  # 标记样式
    alpha: float = 0.7  # 透明度

    # 自动设置标签如果未提供
    @model_validator(mode='after')
    def set_labels(self):
        if self.x_label is None and hasattr(self, 'x_field'):
            self.x_label = self.x_field
        if self.y_label is None and hasattr(self, 'y_field'):
            self.y_label = self.y_field
        return self


class PieChartParams(ColorablePlotParams):
    # 饼图参数模型
    name_field: str = Field(..., description="名称字段，必需")
    value_field: str = Field(..., description="数值字段，必需")
    explode: Optional[List[float]] = None  # 突出显示的扇区
    autopct: Optional[str] = "%1.1f%%"  # 百分比格式
    startangle: int = 90  # 起始角度
    shadow: bool = False  # 是否显示阴影
    labeldistance: float = 1.1  # 标签距离


class HeatMapParams(BasePlotParams):
    # 热力图参数模型
    x_field: str
    y_field: str  # 单个Y轴字段
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    value_field: str = Field(..., description="数值字段，必需")
    color_map: str = 'viridis'  # 颜色映射
    annotate: bool = True  # 是否显示数值
    fmt: str = '.2f'  # 数值格式
    linewidths: float = 0.5  # 网格线宽度
    linecolor: str = 'white'  # 网格线颜色
    aggregation: str = 'mean'  # 聚合函数
    cbar_kws: Optional[dict] = None  # 颜色条的额外参数

    # 自动设置标签如果未提供
    @model_validator(mode='after')
    def set_labels(self):
        if self.x_label is None and hasattr(self, 'x_field'):
            self.x_label = self.x_field
        if self.y_label is None and hasattr(self, 'y_field'):
            self.y_label = self.y_field
        return self


class MermaidChartParams(NoDataBasePlotParams):
    # mermaid图参数模型（特殊处理）
    # mermaid图特有的参数可以在这里添加
    mermaid_code: str = Field(..., description="Mermaid图代码，必需")
    save_path: str = Field(..., description="保存路径，必需，支持png、svg、mmd格式")



def get_params_model(plot_type: str):
    """根据图表类型获取对应的参数模型
    
    Args:
        plot_type: 图表类型字符串
        
    Returns:
        对应的参数模型类
        
    Raises:
        ValueError: 如果图表类型不支持
    """
    model_map = {
        PlotType.LINE_CHART.value: LineChartParams,
        PlotType.BAR_CHART.value: BarChartParams,
        PlotType.PIE_CHART.value: PieChartParams,
        PlotType.SCATTER_PLOT.value: ScatterPlotParams,
        PlotType.HEAT_MAP.value: HeatMapParams,
        PlotType.MERMAID_CHART.value: MermaidChartParams
    }
    
    if plot_type not in model_map:
        raise ValueError(f"不支持的图表类型: {plot_type}")
    
    return model_map[plot_type]


def validate_and_convert_params(plot_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证并转换图表参数
    
    Args:
        plot_type: 图表类型
        params: 参数字典
        
    Returns:
        验证并转换后的参数字典
        
    Raises:
        ValidationError: 如果参数验证失败
    """
    model_cls = get_params_model(plot_type)
    model = model_cls(**params)
    return model.dict()
