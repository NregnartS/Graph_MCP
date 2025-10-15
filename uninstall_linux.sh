#!/usr/bin/env bash
set -euo pipefail

# 卸载脚本（对称于 install_linux.sh）
# 用法：
#   bash uninstall_linux.sh [--purge]
# 说明：
#   - 停止并禁用 systemd --user 服务 graph-mcp.service
#   - 删除用户服务单元文件
#   - 终止残留 Python 进程（匹配 graph_mcp.py 与仓库路径）
#   - 从已存在的客户端配置中移除 MCP server: graph_mcp
#   - --purge 额外删除 .venv、logs、output、.cache

PURGE="0"
if [[ "${1:-}" == "--purge" ]]; then
  PURGE="1"
fi

REPO_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd)"
cd "$REPO_DIR"

echo "[INFO] 停止并禁用 systemd --user 服务"
if command -v systemctl >/dev/null 2>&1; then
  systemctl --user stop graph-mcp.service 2>/dev/null || true
  systemctl --user disable graph-mcp.service 2>/dev/null || true
  UNIT_DIR="$HOME/.config/systemd/user"
  if [[ -f "$UNIT_DIR/graph-mcp.service" ]]; then
    rm -f "$UNIT_DIR/graph-mcp.service"
    echo "[OK] 已删除服务文件 $UNIT_DIR/graph-mcp.service"
  fi
  systemctl --user daemon-reload || true
else
  echo "[WARN] 未检测到 systemctl，跳过 systemd 步骤"
fi

echo "[INFO] 终止可能残留的 Python 进程"
# 仅粗略匹配，避免误杀其它项目
pkill -f "python.*graph_mcp\.py.*$REPO_DIR" 2>/dev/null || true

echo "[INFO] 从客户端配置移除 MCP server: graph_mcp"
# 用 Python 做 JSON 安全修改（不依赖 jq）
python3 - "$REPO_DIR" <<'PY'
import json, os, sys, platform
from pathlib import Path

home = Path.home()
sysname = platform.system().lower()
targets = []

if sysname.startswith("win"):
    # 理论上不会走到这（Linux 脚本），但保留兼容
    appdata = os.getenv("APPDATA") or str(home / "AppData" / "Roaming")
    win = {
        "Cline": (Path(appdata) / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings", "cline_mcp_settings.json"),
        "Roo Code": (Path(appdata) / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings", "mcp_settings.json"),
        "Claude": (Path(appdata) / "Claude", "claude_desktop_config.json"),
        "Cursor": (home / ".cursor", "mcp.json"),
        "Windsurf": (home / ".codeium" / "windsurf", "mcp_config.json"),
        "Claude Code": (home, ".claude.json"),
        "LM Studio": (home / ".lmstudio", "mcp.json"),
        "CodeBuddy IDE": (Path(appdata) / "CodeBuddy" / "User" / "globalStorage" / "tencent.planning-genie" / "settings", "codebuddy_mcp_settings.json"),
        "CodeBuddy CLI": (home, ".codebuddy.json"),
    }
    for _, (d,f) in win.items():
        targets.append(Path(d)/f)
else:
    linux = {
        "Cline": (home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings", "cline_mcp_settings.json"),
        "Roo Code": (home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings", "mcp_settings.json"),
        "Cursor": (home / ".cursor", "mcp.json"),
        "Windsurf": (home / ".codeium" / "windsurf", "mcp_config.json"),
        "Claude Code": (home, ".claude.json"),
        "LM Studio": (home / ".lmstudio", "mcp.json"),
        "CodeBuddy IDE": (home / ".codebuddy-server" / "data" / "User" / "globalStorage" / "tencent.planning-genie" / "settings", "codebuddy_mcp_settings.json"),
        "CodeBuddy CLI": (home, ".codebuddy.json"),
    }
    for _, (d,f) in linux.items():
        targets.append(Path(d)/f)

def load(p: Path):
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        try:
            p.rename(p.with_suffix(p.suffix + ".bak"))
        except Exception:
            pass
    return None

def save(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

changed_any = False
for p in targets:
    if not p.exists():
        continue
    obj = load(p)
    if obj is None:
        continue
    changed = False
    if isinstance(obj, dict):
        ms = obj.get("mcpServers")
        if isinstance(ms, dict) and "graph_mcp" in ms:
            ms.pop("graph_mcp", None)
            changed = True
        sv = obj.get("servers")
        if isinstance(sv, dict) and "graph_mcp" in sv:
            sv.pop("graph_mcp", None)
            changed = True
    if changed:
        save(p, obj)
        print(f"[OK] 移除: {p}")
        changed_any = True

if not changed_any:
    print("[INFO] 未发现需要移除的配置或文件不存在")
PY

if [[ "$PURGE" == "1" ]]; then
  echo "[INFO] Purge 模式：删除 .venv、logs、output、.cache"
  rm -rf ".venv" "logs" "output" ".cache" || true
fi

echo "[OK] 卸载完成。若需完全清理：bash uninstall_linux.sh --purge"