import json
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

# 优先读取 active_mcp_tools.json
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ACTIVE_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'active_mcp_tools.json')
RECOMMENDED_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'recommended_frontend_config.json')

def get_installed_mcp_tools():
    """
    优先从 active_mcp_tools.json 获取所有已安装MCP工具及其描述。
    若不存在则回退到 recommended_frontend_config.json。
    返回格式: List[Dict]，每个dict包含 server, tool, description
    """
    config_path = ACTIVE_CONFIG_PATH if os.path.exists(ACTIVE_CONFIG_PATH) else RECOMMENDED_CONFIG_PATH
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"{config_path} not found")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    tools = []
    servers = config.get("servers", []) or config.get("mcp", {}).get("servers", [])
    for server in servers:
        server_name = server.get("name", "unknown-server")
        for tool in server.get("tools", []):
            tools.append({
                "server": server_name,
                "tool": tool.get("name", "unknown-tool"),
                "description": tool.get("description", "")
            })
    return tools

def build_mcp_tools_section(mcp_tools):
    """
    生成MCP工具说明文本，供插入prompt模板
    """
    if not mcp_tools:
        return "(当前未检测到可用MCP工具)"
    lines = ["当前可用的MCP工具有："]
    for tool in mcp_tools:
        desc = tool["description"] or ""
        lines.append(f"- `{tool['tool']}`（{tool['server']}）：{desc}")
    return "\n".join(lines)

def recommend_tools_for_step(step_title, step_description, mcp_tools):
    """
    根据step内容和工具描述做简单关键词匹配，推荐相关MCP工具。
    返回推荐的工具列表。
    """
    keywords = {
        "memory": ["存储", "实体", "关系", "知识", "图谱", "add", "create", "observation"],
        "file": ["文件", "读取", "写入", "本地", "文档", "read", "write"],
        "analysis": ["分析", "推理", "sequential", "think", "reason"],
        "search": ["检索", "搜索", "查找", "query", "search"],
    }
    matched_tools = []
    text = (step_title or "") + (step_description or "")
    for tool in mcp_tools:
        for k, kws in keywords.items():
            if any(kw in text for kw in kws) and (k in tool["tool"].lower() or k in tool["description"].lower()):
                matched_tools.append(tool)
                break
    return matched_tools

async def call_mcp_tool_with_retry(client, tool_name, *args, **kwargs):
    try:
        return await client.call_tool(tool_name, *args, **kwargs)
    except ClosedResourceError:
        # 尝试重启MCP子进程并重试
        await client.restart()
        return await client.call_tool(tool_name, *args, **kwargs) 