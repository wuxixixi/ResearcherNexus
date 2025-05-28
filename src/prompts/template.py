# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import dataclasses
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.prebuilt.chat_agent_executor import AgentState
from src.config.configuration import Configuration
from src.utils.mcp_tools import get_installed_mcp_tools, build_mcp_tools_section, recommend_tools_for_step
import logging

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

# Initialize logger
logger = logging.getLogger(__name__)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str, state: AgentState, configurable: Configuration = None
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    # Add configurable variables
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    # 动态插入MCP工具说明
    if prompt_name == "planner":
        # mcp_tools = get_installed_mcp_tools() # 旧的调用方式
        
        # === 新逻辑：从 configurable.mcp_settings 构建工具列表 ===
        current_mcp_tools = []
        if configurable and configurable.mcp_settings and "servers" in configurable.mcp_settings:
            for server_name, server_config in configurable.mcp_settings["servers"].items():
                if "enabled_tools" in server_config and isinstance(server_config["enabled_tools"], list):
                    # 尝试从 server_config 中直接获取工具的描述信息。
                    # 这取决于 configurable.mcp_settings 中服务器和工具的详细结构。
                    # 我们需要确保输出的 mcp_tools 列表中的每个字典都有 "tool", "server", 和 "description" 键，
                    # 以便 build_mcp_tools_section 可以正确工作。
                    
                    # 查找工具描述的逻辑可能需要适配您的配置结构
                    # 假设 server_config["tools"] (如果存在且是列表) 包含每个工具的详细信息，包括描述
                    # 或者 enabled_tools 就是工具名列表，描述需要特殊处理
                    
                    # 简化处理：如果 server_config 中直接有 tools 列表且包含描述
                    # （这需要您的 configurable.mcp_settings 结构支持）
                    # 否则，我们可能需要像 planner_node 中那样生成一个临时描述
                    
                    # 方案1: 尝试从一个假设的更详细的工具定义中获取描述
                    # 这需要 configurable.mcp_settings[server_name] 内部有一个 "tools_details" (或其他名字) 列表
                    # tools_details_map = {t.get("name"): t.get("description", "") 
                    #                        for t in server_config.get("tools_details", []) if isinstance(t, dict)}

                    for tool_name in server_config["enabled_tools"]:
                        description = f"Tool {tool_name} from server {server_name}" # 默认/回退描述
                        # if tool_name in tools_details_map:
                        #    description = tools_details_map[tool_name]
                        
                        # 另一种可能性：如果 server_config 本身就是 active_mcp_tools.json 中那种服务器条目的结构，
                        # 它可能直接有一个 "tools" 列表，其中每个元素是 {'name': '...', 'description': '...'}
                        # 我们需要检查 server_config 的结构
                        # 假设 enabled_tools 是字符串列表, 我们从这里获取工具名
                        # 描述的来源是这里的关键。
                        # 为了与 build_mcp_tools_section 兼容，必须提供 description。

                        # 查找该工具在原始配置中的描述 (如果您的配置结构支持)
                        # 例如, 如果 configurable.mcp_settings[server_name]['tools_definitions'] 是一个像 active_mcp_tools.json['servers'][i]['tools'] 那样的列表:
                        found_description = f"(Description for {tool_name} not directly available in current settings structure)"
                        if isinstance(server_config.get("tools"), list): # 检查是否存在一个详细的 tools 列表
                            for tool_detail in server_config.get("tools", []):
                                if isinstance(tool_detail, dict) and tool_detail.get("name") == tool_name:
                                    found_description = tool_detail.get("description", found_description)
                                    break
                        elif "description" in server_config: # 或者服务器级别有一个通用描述？不太可能用于单个工具
                            pass 
                            
                        current_mcp_tools.append({
                            "tool": tool_name,
                            "server": server_name,
                            "description": found_description # 使用找到的描述或回退描述
                        })
        # === END 新逻辑 ===
        # 调试打印：显示为 DYNAMIC_MCP_TOOLS_SECTION 准备的工具列表
        logger.info(f"[DEBUG] Tools for DYNAMIC_MCP_TOOLS_SECTION: {current_mcp_tools}")
        state_vars["DYNAMIC_MCP_TOOLS_SECTION"] = build_mcp_tools_section(current_mcp_tools)

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")
