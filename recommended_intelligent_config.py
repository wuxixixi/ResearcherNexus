#!/usr/bin/env python3
"""
推荐的智能MCP配置

使用方法：
1. 在研究工作流中使用这个配置
2. 系统会根据研究内容自动选择工具
3. 无需手动指定add_to_agents
"""

# 智能工具选择配置
INTELLIGENT_MCP_CONFIG = {
    "mcp_settings": {
        "servers": {
            "memory-server": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "@modelcontextprotocol/server-memory"
                ],
                "enabled_tools": [
                    "create_entities",
                    "create_relations",
                    "add_observations",
                    "delete_entities",
                    "delete_observations",
                    "delete_relations"
                ]
            }
        }
    }
}

# 使用示例
def get_research_config(thread_id="auto_generated"):
    return {
        "configurable": {
            "thread_id": thread_id,
            "max_plan_iterations": 2,
            "max_step_num": 5,
            "max_search_results": 5,
            **INTELLIGENT_MCP_CONFIG
        },
        "recursion_limit": 100
    }

if __name__ == "__main__":
    print("🎯 推荐的智能MCP配置:")
    print(json.dumps(INTELLIGENT_MCP_CONFIG, indent=2, ensure_ascii=False))
