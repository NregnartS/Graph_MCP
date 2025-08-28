#!/bin/bash

# 快速启动脚本 - 用于启动FastMCP绘图服务

# 检查Python环境
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d '.' -f 1,2)
REQUIRED_VERSION=3.10

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
  echo "错误: Python版本需要3.10或更高版本，当前版本为$PYTHON_VERSION"
  exit 1
fi

echo "Python环境检查通过 (版本: $PYTHON_VERSION)"

# 启动服务器
echo "正在启动FastMCP绘图服务..."
python src/main.py