#!/bin/bash

# 启动FastMCP绘图服务的脚本

# 默认端口号
DEFAULT_PORT=16666

# 显示帮助信息
show_help() {
    echo "使用方法: $0 [-p 端口号] [-d] [-h]"
    echo "选项:"
    echo "  -p, --port       指定服务端口号，默认为 $DEFAULT_PORT"
    echo "  -d, --debug      启用调试模式"
    echo "  -h, --help       显示帮助信息"
    exit 0
}

# 解析命令行参数
PORT=""
DEBUG=""
while getopts "p:dh" opt; do
  case $opt in
    p) PORT="--port $OPTARG" ;;
    d) DEBUG="--debug" ;;
    h) show_help ;;
    *) echo "错误: 未知选项 $opt"
       show_help ;;
  esac
done

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python环境，请先安装Python 3.10或更高版本"
        exit 1
    fi
    PYTHON="python"
else
    PYTHON="python3"
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}' | cut -d '.' -f 1,2)
REQUIRED_VERSION=3.10

# 比较版本号
if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
  echo "错误: Python版本需要3.10或更高版本，当前版本为$PYTHON_VERSION"
  exit 1
fi

echo "Python环境检查通过 (版本: $PYTHON_VERSION)"

# 确保项目目录下有main.py
if [ ! -f main.py ]; then
    echo "错误: 未找到main.py文件，当前目录可能不是项目根目录"
    exit 1
fi

# 创建必要的目录
LOG_DIR="logs"
OUTPUT_DIR="output"
CACHE_DIR=".cache"

mkdir -p $LOG_DIR $OUTPUT_DIR $CACHE_DIR

echo "必要的目录已创建: $LOG_DIR, $OUTPUT_DIR, $CACHE_DIR"

# 启动服务
echo "正在启动FastMCP绘图服务..."

if [ -z "$PORT" ]; then
  echo "使用默认端口 $DEFAULT_PORT"
  SERVER_ARGS="--port $DEFAULT_PORT $DEBUG"
else
  echo "使用指定端口 ${OPTARG}"
  SERVER_ARGS="$PORT $DEBUG"
fi

if [ -n "$DEBUG" ]; then
    echo "调试模式: 已启用"
fi

# 启动服务器并记录日志
$PYTHON main.py $SERVER_ARGS

# 如果服务器意外退出，显示错误信息
if [ $? -ne 0 ]; then
    echo "错误: FastMCP绘图服务启动失败，请查看日志获取详细信息"
    exit 1
fi