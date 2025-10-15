#!/usr/bin/env bash
set -euo pipefail

# 安装与后台运行（systemd 用户服务）脚本
# 用法：
#   bash install_linux.sh [-p PORT] [--debug]
# 例：
#   bash install_linux.sh -p 18888
#
# 完成操作：
# 1) 创建虚拟环境并安装依赖
# 2) 生成并启用 systemd --user 服务 graph-mcp.service
# 3) 写入/更新各大 Agent 的 MCP 配置文件
#
# 依赖：Python 3.10+、systemd (用户服务)

PORT=16666
DEBUG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

REPO_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
cd "$REPO_DIR"

if ! command -v python3 >/dev/null; then
  echo "需要 python3 (3.10+)"; exit 1
fi

PYVER=$(python3 -c 'import sys;print(".".join(map(str,sys.version_info[:2])))')
python3 -c 'import sys;exit(0) if sys.version_info>=(3,10) else exit(1)' || { echo "Python 版本需≥3.10，当前: $PYVER"; exit 1; }

# 1) 虚拟环境 + 依赖
# 确保 .venv/bin/activate 存在；若损坏则重建；若缺少 venv 模块则给出提示
if [[ ! -f ".venv/bin/activate" ]]; then
  if [[ -d ".venv" && ! -f ".venv/bin/activate" ]]; then
    echo "检测到损坏的虚拟环境，正在重新创建 .venv ..."
    rm -rf .venv
  fi
  if ! python3 -m venv .venv 2>/dev/null; then
    echo "创建虚拟环境失败。可能缺少 python3-venv 包。"
    echo "请安装后重试：sudo apt-get update && sudo apt-get install -y python3-venv"
    exit 1
  fi
fi

# 再次校验激活脚本
if [[ ! -f ".venv/bin/activate" ]]; then
  echo "虚拟环境创建后仍缺少 .venv/bin/activate，退出。"
  exit 1
fi

source .venv/bin/activate
python -m pip install -U pip
if [[ -f "requirements.txt" ]]; then
  pip install -r requirements.txt
else
  echo "警告：未找到 requirements.txt，跳过依赖安装。"
fi

mkdir -p logs output .cache

# 2) 生成 systemd 用户服务
UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$UNIT_DIR"

# 写入服务文件
cat >"$UNIT_DIR/graph-mcp.service" <<'EOF'
[Unit]
Description=Graph MCP plotting service (user)
After=default.target

[Service]
Type=simple
WorkingDirectory=__WORKDIR__
Environment=PATH=__WORKDIR__/.venv/bin:%h/.local/bin:/usr/local/bin:/usr/bin
Environment=GRAPH_MCP_PORT=__PORT__
ExecStart=__WORKDIR__/.venv/bin/python graph_mcp.py --port __PORT__ __DEBUG__
Restart=always
RestartSec=5
StandardOutput=append:__WORKDIR__/logs/service.out.log
StandardError=append:__WORKDIR__/logs/service.err.log

[Install]
WantedBy=default.target
EOF

# 替换占位符
sed -i "s#__WORKDIR__#${REPO_DIR}#g" "$UNIT_DIR/graph-mcp.service"
sed -i "s#__PORT__#${PORT}#g" "$UNIT_DIR/graph-mcp.service"
if [[ -n "$DEBUG" ]]; then
  sed -i "s#__DEBUG__#--debug#g" "$UNIT_DIR/graph-mcp.service"
else
  sed -i "s#__DEBUG__##g" "$UNIT_DIR/graph-mcp.service"
fi

# 重新加载并启用服务
systemctl --user daemon-reload
systemctl --user enable --now graph-mcp.service

# 3) 写入 MCP 配置
.venv/bin/python scripts/setup_mcp_configs.py --port "$PORT"

echo "安装完成。管理命令（用户服务）："
echo "  查看状态: systemctl --user status graph-mcp.service"
echo "  查看日志: tail -f logs/service.out.log logs/service.err.log"
echo "  重启服务: systemctl --user restart graph-mcp.service"
echo "  停止服务: systemctl --user stop graph-mcp.service"