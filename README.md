# FastMCP 绘图服务

这是一个基于FastMCP的本地绘图服务，提供多种图表生成功能，支持中文字体显示。

## 功能特性

- **折线图**：支持多条线、自定义颜色、标题和标签
- **柱状图**：支持多组数据对比、自定义颜色和宽度
- **饼图**：支持显示百分比、自定义颜色
- **散点图**：支持颜色编码、大小编码
- **热力图**：用于展示矩阵数据的热力分布
- **Mermaid图表**：默认优先使用mermaid-cli（高性能）生成图表，如未安装则使用mermaid-py库作为备选方案，支持生成Mermaid流程图、时序图等

## 安装指南

### 前提条件
- Python 3.10+ 
- Conda环境（推荐使用fastmcp_env环境）
- Node.js（可选，用于安装mermaid-cli以获得更好的Mermaid图表生成性能）

### 安装步骤

1. 克隆或下载项目代码

2. 安装项目依赖
#### 安装python依赖
   **方式一：使用pip安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
   
   **方式二：使用conda和environment.yml生成虚拟环境**（推荐）
   ```bash
   # 创建并激活conda虚拟环境（默认安装路径）
   conda env create -f environment.yml
   conda activate fastmcp_env
   
   # 或指定安装路径
   conda env create -f environment.yml --prefix /path/to/your/environment
   conda activate /path/to/your/environment
   ```
   
   说明：
   - 默认情况下，环境会安装在conda的envs目录下
   - 使用--prefix参数可以自定义环境安装路径
   - 激活自定义路径的环境时需要使用完整路径

#### 安装mermaid-cli（可选但推荐）

  mermaid-cli提供比mermaid-py更好的性能和稳定性，我们建议安装它以获得最佳体验：

  ```bash
  # 使用npm全局安装mermaid-cli
  npm install -g @mermaid-js/mermaid-cli

  # 验证安装是否成功
  mmdc --version
  ```

  **注意**：安装mermaid-cli需要先安装Node.js。如果您的系统尚未安装Node.js，请先从[Node.js官网](https://nodejs.org/)下载并安装。

  如果未安装mermaid-cli，系统会自动使用requirements.txt中已包含的mermaid-py库作为备选方案。

## 使用方法

### 启动服务器

您可以通过以下方式启动服务器：

```bash
# 使用默认端口（16666）启动
./start_server.sh

# 使用指定端口启动
./start_server.sh -p 自定义端口号

# 查看帮助信息
./start_server.sh -h
```

服务器默认将在 http://0.0.0.0:16666 启动。如果使用了自定义端口，则会在指定端口启动。

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

## 注意事项

1. 所有接口都支持中文字体显示
2. 图表会保存为指定路径的文件
3. 系统会自动创建不存在的目录
4. 文件路径会进行严格的合法性校验
5. 参数会通过pydantic模型进行验证
6. 如需自定义更多样式，请修改`plotting_tools.py`文件中的相关代码