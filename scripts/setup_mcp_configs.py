#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
import platform
from pathlib import Path
import argparse

def ensure_parent(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def load_json(p: Path):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            # 备份损坏文件
            try:
                p.rename(p.with_suffix(p.suffix + ".bak"))
            except Exception:
                pass
    return {}

def save_json(p: Path, data: dict):
    ensure_parent(p)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def merge_mcp_server(doc: dict, name: str, server_cfg: dict):
    # 通用位置：mcpServers 顶层字典
    m = doc.get("mcpServers")
    if not isinstance(m, dict):
        doc["mcpServers"] = {}
        m = doc["mcpServers"]
    m[name] = server_cfg

    # 兼容性：某些工具可能使用 "servers" 键
    s = doc.get("servers")
    if isinstance(s, dict):
        s[name] = server_cfg
    return doc

def get_default_paths():
    home = Path.home()
    sysname = platform.system().lower()
    paths = {}
    if sysname.startswith("win"):
        appdata = os.getenv("APPDATA") or str(home / "AppData" / "Roaming")
        win_configs = {
            "Cline": (Path(appdata) / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings", "cline_mcp_settings.json"),
            "Roo Code": (Path(appdata) / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings", "mcp_settings.json"),
            "Claude": (Path(appdata) / "Claude", "claude_desktop_config.json"),
            "Cursor": (home / ".cursor", "mcp.json"),
            "Windsurf": (home / ".codeium" / "windsurf", "mcp_config.json"),
            "Claude Code": (home, ".claude.json"),
            "LM Studio": (home / ".lmstudio", "mcp.json"),
            "CodeBuddy IDE": (Path(appdata) / "CodeBuddy" / "User" / "globalStorage" / "tencent.planning-genie" / "settings", "codebuddy_mcp_settings.json"),
            "CodeBuddy CLI": (home, ".codebuddy.json"),
            "Trae CN": (Path(appdata) / "Trae CN" / "User", "mcp.json"),
        }
        for k, (d, f) in win_configs.items():
            paths[k] = Path(d) / f
    else:
        linux_configs = {
            "Cline": (home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings", "cline_mcp_settings.json"),
            "Roo Code": (home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings", "mcp_settings.json"),
            "Cursor": (home / ".cursor", "mcp.json"),
            "Windsurf": (home / ".codeium" / "windsurf", "mcp_config.json"),
            "Claude Code": (home, ".claude.json"),
            "LM Studio": (home / ".lmstudio", "mcp.json"),
            "CodeBuddy IDE": (home / ".codebuddy-server" / "data" / "User" / "globalStorage" / "tencent.planning-genie" / "settings", "codebuddy_mcp_settings.json"),
            "CodeBuddy CLI": (home, ".codebuddy.json"),
        }
        for k, (d, f) in linux_configs.items():
            paths[k] = Path(d) / f
    return paths

def build_server_entry(project_root: Path, port: int):
    # 使用 URL 形式的 streamableHttp 配置
    return {
        "type": "streamableHttp",
        "url": f"http://127.0.0.1:{port}/mcp"
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.getenv("GRAPH_MCP_PORT", "16666")))
    parser.add_argument("--name", type=str, default="graph_mcp")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    server_entry = build_server_entry(project_root, args.port)

    targets = get_default_paths()
    wrote = []
    skipped = []
    for app, p in targets.items():
        try:
            # 仅在配置文件已存在时写入，避免为未安装的客户端创建文件
            if not p.exists():
                skipped.append(str(p))
                continue
            doc = load_json(p)
            doc = merge_mcp_server(doc, args.name, server_entry)
            save_json(p, doc)
            wrote.append(str(p))
        except Exception as e:
            # 尽量不中断其它目标
            print(f"[WARN] 写入 {app} 失败: {e}", file=sys.stderr)

    # 另存一份模板
    tmpl = {
        "mcpServers": {
            args.name: server_entry
        }
    }
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "mcp_config_example.json").write_text(json.dumps(tmpl, ensure_ascii=False, indent=2), encoding="utf-8")

    print("已更新/创建 MCP 配置（已存在的目标）：")
    for p in wrote:
        print("  -", p)
    if skipped:
        print("以下路径未写入（文件不存在，可能未安装对应客户端）：")
        for p in skipped:
            print("  -", p)
    print("其余client可自行手动添加json配置")
    print("json配置示例见 output/mcp_config_example.json")

if __name__ == "__main__":
    main()