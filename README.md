# FastMCP 绘图服务

一个基于FastMCP的高性能、模块化图表生成服务，支持多种图表类型和自定义配置。

## 项目特点

- **模块化设计**：清晰的代码结构，便于维护和扩展
- **丰富的图表类型**：支持折线图、柱状图、饼图、散点图、热力图和Mermaid图
- **中文字体支持**：自动检测和配置系统中的中文字体
- **主题切换**：支持多种图表主题，满足不同场景需求
- **增强的参数验证**：完善的参数验证和错误处理
- **灵活的配置选项**：丰富的自定义选项，满足各种图表需求

## 项目结构

```
graph_all/
├── src/                    # 源代码目录
│   ├── charts/             # 图表类型实现
│   │   ├── line_chart.py   # 折线图
│   │   ├── bar_chart.py    # 柱状图
│   │   ├── pie_chart.py    # 饼图
│   │   ├── scatter_plot.py # 散点图
│   │   ├── heatmap.py      # 热力图
│   │   └── mermaid_chart.py # Mermaid图
│   ├── utils/              # 工具函数
│   │   ├── font_utils.py   # 字体管理
│   │   ├── file_utils.py   # 文件操作
│   │   └── validation_utils.py # 参数验证
│   └── plotting_base.py    # 绘图基类
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明文档
```

## 功能特性

- **折线图**：支持多条线、自定义颜色、标题和标签、线条样式和标记
- **柱状图**：支持多组数据对比、自定义颜色和宽度、堆叠显示、水平/垂直显示
- **饼图**：支持显示百分比、自定义颜色、扇区突出显示、图例控制
- **散点图**：支持颜色编码、大小编码、自定义标记和透明度
- **热力图**：用于展示矩阵数据的热力分布、支持数据聚合和注释
- **Mermaid图表**：默认优先使用mermaid-cli（高性能）生成图表，如未安装则使用mermaid-py库作为备选方案，支持生成流程图、时序图等
- **中文字体自动检测**：自动搜索系统中可用的中文字体并配置
- **多主题支持**：Mermaid图表支持专用主题，其他图表支持所有Matplotlib内置主题

## 安装指南

### 环境要求
- Python 3.10+ 
- 依赖库：详见 requirements.txt

### 安装步骤

1. 克隆项目代码

```bash
git clone <项目仓库地址>
cd graph_all
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 安装Mermaid CLI（可选，用于生成Mermaid图表）

```bash
# 使用npm安装
npm install -g @mermaid-js/mermaid-cli

# 或者使用yarn
# yarn global add @mermaid-js/mermaid-cli

# 验证安装是否成功
mmdc --version
```

**注意**：安装mermaid-cli需要先安装Node.js。如果未安装mermaid-cli，系统会自动使用mermaid-py库作为备选方案。

## 使用说明

### 启动服务

```bash
python main.py [--port 端口号] [--debug]
```

参数说明：
- `--port`：指定服务端口，默认16666
- `--debug`：启用调试模式，显示更详细的日志

## 图表类型与参数

### 通用参数

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| data | list | 数据列表，每个元素为字典 | 是（除Mermaid图外） |
| save_path | string | 图表保存路径（绝对路径） | 是 |
| title | string | 图表标题 | 否，默认为"图表标题" |
| figsize | tuple | 图表尺寸，如(10, 6) | 否 |
| dpi | int | 分辨率（仅适用于非Mermaid图表） | 否，默认为100 |
| theme | string | 图表主题（Mermaid支持'default', 'dark', 'forest', 'neutral'；其他图表支持所有Matplotlib内置主题） | 否，默认为"default" |

### 折线图（line_chart）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| x_field | string | X轴字段名 | 是 |
| y_fields | list/string | Y轴字段名列表，支持多个字段 | 是 |
| x_label | string | X轴标签 | 否，默认使用x_field值 |
| y_label | string | Y轴标签 | 否 |
| line_styles | list | 线条样式列表 | 否 |
| markers | list | 标记样式列表 | 否 |
| line_widths | list | 线条宽度列表 | 否 |
| colors | list | 颜色列表 | 否 |
| grid | bool | 是否显示网格 | 否，默认为True |

### 柱状图（bar_chart）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| x_field | string | X轴字段名 | 是 |
| y_fields | list/string | Y轴字段名列表，支持多个字段 | 是 |
| x_label | string | X轴标签 | 否，默认使用x_field值 |
| y_label | string | Y轴标签 | 否 |
| bar_width | float | 柱状宽度，范围0-1 | 否，默认为0.8 |
| stack | bool | 是否堆叠显示 | 否，默认为False |
| edge_color | string | 边框颜色 | 否，默认为'black' |
| edge_width | float | 边框宽度 | 否，默认为0.5 |
| horizontal | bool | 是否水平显示 | 否，默认为False |
| colors | list | 颜色列表 | 否 |
| grid | bool | 是否显示网格 | 否，默认为True |

### 饼图（pie_chart）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| name_field | string | 名称字段 | 是 |
| value_field | string | 数值字段 | 是 |
| explode | list | 突出显示的扇区列表 | 否，默认全0 |
| autopct | string | 百分比格式 | 否，默认为"%1.1f%%" |
| start_angle | int | 起始角度 | 否，默认为90 |
| shadow | bool | 是否显示阴影 | 否，默认为False |
| labeldistance | float | 标签距离 | 否，默认为1.1 |
| colors | list | 颜色列表 | 否 |

### 散点图（scatter_plot）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| x_field | string | X轴字段名 | 是 |
| y_field | string | Y轴字段名 | 是 |
| x_label | string | X轴标签 | 否，默认使用x_field值 |
| y_label | string | Y轴标签 | 否，默认使用y_field值 |
| color_field | string | 颜色分组字段 | 否 |
| size_field | string | 点大小字段 | 否 |
| color_map | string | 颜色映射 | 否，默认为'viridis' |
| marker_style | string | 标记样式 | 否，默认为'o' |
| alpha | float | 透明度，范围0-1 | 否，默认为0.7 |
| grid | bool | 是否显示网格 | 否，默认为True |

### 热力图（heatmap）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| x_field | string | X轴字段名 | 是 |
| y_field | string | Y轴字段名 | 是 |
| value_field | string | 数值字段 | 是 |
| x_label | string | X轴标签 | 否，默认使用x_field值 |
| y_label | string | Y轴标签 | 否，默认使用y_field值 |
| color_map | string | 颜色映射 | 否，默认为'viridis' |
| annotate | bool | 是否显示数值 | 否，默认为True |
| fmt | string | 数值格式 | 否，默认为'.2f' |
| linewidths | float | 网格线宽度 | 否，默认为0.5 |
| linecolor | string | 网格线颜色 | 否，默认为'white' |
| aggregation | string | 聚合函数 | 否，默认为'mean'，可选：'mean', 'sum', 'max', 'min', 'count' |

### Mermaid图（mermaid_chart）

| 参数名 | 类型 | 说明 | 是否必需 |
|--------|------|------|----------|
| mermaid_code | string | Mermaid图代码 | 是 |
| save_path | string | 图表保存路径（支持png、svg、mmd格式） | 是 |
| width | int | 图像宽度 | 否，默认为800 |
| height | int | 图像高度 | 否，默认为600 |
| theme | string | 图表主题（支持'default', 'dark', 'forest', 'neutral'） | 否，默认为"default" |

## 支持的主题

### Mermaid图表主题
- `default`: 默认主题
- `dark`: 深色主题
- `forest`: 森林主题
- `neutral`: 中性主题

### Matplotlib图表主题
支持所有Matplotlib内置主题，包括但不限于：
- `default`: 默认主题
- `dark_background`: 深色背景主题
- `classic`: 经典主题
- `seaborn`: Seaborn风格主题
- `ggplot`: ggplot风格主题

## MCP Client端配置

以下是连接到本服务的MCP Client端配置JSON模板：

```json
{
  "mcpServers": {
    "graph_service": {
      "url": "http://127.0.0.1:16666/mcp"
    }
  }
}
```

## 开发说明

### 代码风格
- 遵循PEP 8规范
- 使用type hints进行类型标注
- 添加适当的文档字符串

## 常见问题

### Q: 中文字体显示不正常怎么办？
A: 服务会自动检测系统中的中文字体，如果没有找到合适的字体，可以在`font_utils.py`中手动指定字体路径。

### Q: Mermaid图表生成失败怎么办？
A: 确保已安装Mermaid CLI，或者使用mermaid-py库作为替代方案。



## 注意事项

1. 所有接口都支持中文字体显示
2. 图表会保存为指定路径的文件
3. 使用时请确保保存路径有写权限
4. 系统会自动创建不存在的目录
5. 文件路径会进行严格的合法性校验
6. 参数会通过专门的验证工具进行验证

## 许可证

[MIT License](LICENSE)