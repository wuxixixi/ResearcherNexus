import json
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan, StepType
from src.prompts.template import apply_prompt_template
from src.citations import CitationCollector
from src.utils.json_utils import repair_json_output, sanitize_tool_response
from src.utils.mcp_tools import get_installed_mcp_tools, recommend_tools_for_step

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    task_title: Annotated[str, "The title of the task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


def background_investigation_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner"]]:
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke({"query": query})
        background_investigation_results = None
        if isinstance(searched_content, list):
            background_investigation_results = [
                {"title": elem["title"], "content": elem["content"]}
                for elem in searched_content
            ]
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return Command(
        update={
            "background_investigation_results": json.dumps(
                background_investigation_results, ensure_ascii=False
            )
        },
        goto="planner",
    )


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter", "enhanced_reporter"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = apply_prompt_template("planner", state, configurable)

    if (
        plan_iterations == 0
        and state.get("enable_background_investigation")
        and state.get("background_investigation_results")
    ):
        messages += [
            {
                "role": "user",
                "content": (
                    "background investigation results of user query:\n"
                    + state["background_investigation_results"]
                    + "\n"
                ),
            }
        ]

    llm = get_llm_by_type(AGENT_LLM_MAP["planner"])

    # 统一使用llm.stream(messages)，兼容openrouter流式返回格式
    response = llm.stream(messages)
    full_response = ""
    for chunk in response:
        if hasattr(chunk, 'content') and chunk.content:
            full_response += chunk.content
        else:
            logger.warning(f"[openrouter流式兼容] 跳过无content字段的chunk: {chunk}")
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")

    try:
        curr_plan = json.loads(repair_json_output(full_response))
        
        # === 修改：从 configurable.mcp_settings 构建工具列表 ===
        available_mcp_tools = []
        if configurable.mcp_settings and "servers" in configurable.mcp_settings:
            for server_name, server_config in configurable.mcp_settings["servers"].items():
                if "enabled_tools" in server_config and isinstance(server_config["enabled_tools"], list):
                    # Prepare a map of tool_name to description from the detailed tools list, if available
                    tool_descriptions = {}
                    if "tools" in server_config and isinstance(server_config["tools"], list):
                        for tool_detail in server_config["tools"]:
                            if isinstance(tool_detail, dict) and "name" in tool_detail:
                                tool_descriptions[tool_detail["name"]] = tool_detail.get("description", "")

                    for tool_name in server_config["enabled_tools"]:
                        description = tool_descriptions.get(tool_name, f"Tool {tool_name} from server {server_name} (description not found)")
                        available_mcp_tools.append({
                            "tool": tool_name, 
                            "description": description
                        }) 

        # 调试打印：显示 planner_node 为 recommend_tools_for_step 准备的工具列表
        logger.info(f"[DEBUG] Tools for recommend_tools_for_step in planner_node: {available_mcp_tools}")
        # mcp_tools = get_installed_mcp_tools() # 旧的调用方式
        for step in curr_plan.get("steps", []):
            recommended = recommend_tools_for_step(step.get("title", ""), step.get("description", ""), available_mcp_tools) # 使用新的工具列表
            if recommended:
                # 确认 recommend_tools_for_step 返回的推荐列表中每个字典的工具名键是否也是 "tool"
                # 如果是，则这里也应该用 t["tool"]
                tool_str = ", ".join(f'`{t["tool"]}`' for t in recommended) # 确认使用 "tool" 键
                step["description"] = step.get("description", "") + f"\n\n建议使用的MCP工具：{tool_str}"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            # 检查是否启用增强版报告员
            use_enhanced_reporter = config.get("configurable", {}).get("use_enhanced_reporter", False)
            return Command(goto="enhanced_reporter" if use_enhanced_reporter else "reporter")
        else:
            return Command(goto="__end__")
    if curr_plan.get("has_enough_context"):
        logger.info("Planner response has enough context.")
        new_plan = Plan.model_validate(curr_plan)
        # 检查是否启用增强版报告员
        use_enhanced_reporter = config.get("configurable", {}).get("use_enhanced_reporter", False)
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],
                "current_plan": new_plan,
            },
            goto="enhanced_reporter" if use_enhanced_reporter else "reporter",
        )
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner")],
            "current_plan": full_response,
        },
        goto="human_feedback",
    )


def human_feedback_node(
    state, config: RunnableConfig = None
) -> Command[Literal["planner", "research_team", "reporter", "enhanced_reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")

        # if the feedback is not accepted, return the planner node
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # increment the plan iterations
        plan_iterations += 1
        # parse the plan
        new_plan = json.loads(current_plan)
        if new_plan["has_enough_context"]:
            # 检查是否启用增强版报告员
            use_enhanced_reporter = config.get("configurable", {}).get("use_enhanced_reporter", False) if config else False
            goto = "enhanced_reporter" if use_enhanced_reporter else "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            # 检查是否启用增强版报告员
            use_enhanced_reporter = config.get("configurable", {}).get("use_enhanced_reporter", False) if config else False
            return Command(goto="enhanced_reporter" if use_enhanced_reporter else "reporter")
        else:
            return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )


def coordinator_node(
    state: State,
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner])
        .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified

    if len(response.tool_calls) > 0:
        goto = "planner"
        if state.get("enable_background_investigation"):
            # if the search_before_planning is True, add the web search tool to the planner agent
            goto = "background_investigator"
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_locale := tool_call.get("args", {}).get("locale"):
                    locale = tool_locale
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    return Command(
        update={"locale": locale},
        goto=goto,
    )


async def enhanced_reporter_node(state: State, config: RunnableConfig):
    """Enhanced reporter node with MCP tools support for better report generation."""
    logger.info("Enhanced reporter generating final report with MCP tools")
    
    # 获取配置和基础信息
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])
    
    # 准备基础工具
    default_tools = [
        get_web_search_tool(configurable.max_search_results),  # 用于事实核查
        crawl_tool,  # 用于深度信息获取
    ]
    
    # 准备报告员的输入数据，模拟一个"报告生成"步骤
    reporter_input = {
        "messages": [
            HumanMessage(
                content=f"# Report Generation Task\n\n## Research Topic\n\n{current_plan.title}\n\n## Research Description\n\n{current_plan.thought}\n\n## Research Findings\n\n" + 
                "\n\n".join([f"### Finding {i+1}\n{obs}" for i, obs in enumerate(observations)]) +
                f"\n\n## Instructions\n\nGenerate a comprehensive research report based on the above findings. Use available tools to verify key facts, fill information gaps, and enhance the report quality. Ensure all information is accurate and up-to-date.\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }
    
    # 创建一个临时的"步骤"来处理报告生成
    from src.prompts.planner_model import Step, StepType
    temp_step = Step(
        title="Generate Enhanced Research Report",
        description="Create a comprehensive research report using available tools for fact-checking and information enhancement",
        step_type=StepType.RESEARCH,
        execution_res=None
    )
    
    # 临时修改状态以包含这个步骤
    temp_plan = current_plan.model_copy()
    temp_plan.steps = [temp_step]
    temp_state = state.copy()
    temp_state["current_plan"] = temp_plan
    
    # 使用增强版报告员的MCP工具配置逻辑
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for reporter agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and "reporter" in server_config.get("add_to_agents", [])
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        try:
            async with MultiServerMCPClient(mcp_servers) as client:
                loaded_tools = default_tools[:]
                for tool in client.get_tools():
                    if tool.name in enabled_tools:
                        tool.description = (
                            f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                        )
                        loaded_tools.append(tool)
                
                # 创建增强版报告员代理，使用专门的提示模板
                agent = create_agent("enhanced_reporter", "enhanced_reporter", loaded_tools, "enhanced_reporter")
                
                # 执行报告生成
                result = await agent.ainvoke(
                    input=reporter_input, 
                    config={"recursion_limit": 25}
                )
                
                # 提取报告内容
                response_content = result["messages"][-1].content
                # logger.info(f"Enhanced reporter response: {response_content}") # 暂时注释掉
                
                return {"final_report": response_content}
                
        except Exception as e:
            logger.warning(f"Failed to start MCP servers for enhanced reporter: {e}. Using default tools instead.")
            # Fall back to default tools if MCP server startup fails
            agent = create_agent("enhanced_reporter", "enhanced_reporter", default_tools, "enhanced_reporter")
            result = await agent.ainvoke(
                input=reporter_input, 
                config={"recursion_limit": 25}
            )
            response_content = result["messages"][-1].content
            # logger.info(f"Enhanced reporter fallback response: {response_content}") # 暂时注释掉，区分于MCP成功的情况
            return {"final_report": response_content}
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent("enhanced_reporter", "enhanced_reporter", default_tools, "enhanced_reporter")
        result = await agent.ainvoke(
            input=reporter_input, 
            config={"recursion_limit": 25}
        )
        response_content = result["messages"][-1].content
        # logger.info(f"Enhanced reporter default tools response: {response_content}") # 暂时注释掉
        return {"final_report": response_content}


def reporter_node(state: State):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    current_plan = state.get("current_plan")
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_)
    observations = state.get("observations", [])

    # Add a reminder about the new report format, citation style, and table usage
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
            name="system",
        )
    )

    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    # logger.debug(f"Current invoke messages: {invoke_messages}") # 暂时注释掉
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    response_content = response.content
    # logger.info(f"reporter response: {response_content}") # 暂时注释掉

    return {"final_report": response_content}


def research_team_node(
    state: State,
) -> Command[Literal["planner", "researcher", "coder"]]:
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return Command(goto="planner")
    if all(step.execution_res for step in current_plan.steps):
        return Command(goto="planner")
    for step in current_plan.steps:
        if not step.execution_res:
            break
    if step.step_type and step.step_type == StepType.RESEARCH:
        return Command(goto="researcher")
    if step.step_type and step.step_type == StepType.PROCESSING:
        return Command(goto="coder")
    return Command(goto="planner")


def _get_intelligent_tool_recommendations(step_title: str, step_description: str, agent_type: str) -> dict:
    """
    Intelligently recommend MCP tools based on the research step content and agent type.
    
    Args:
        step_title: The title of the current research step
        step_description: The description of the current research step
        agent_type: The type of agent ("researcher" or "coder")
    
    Returns:
        Dictionary with recommended tool categories and priorities
    """
    content = f"{step_title} {step_description}".lower()
    
    # Define tool recommendation patterns with both English and Chinese keywords
    tool_patterns = {
        # Memory and knowledge management
        "memory": {
            "keywords": [
                # English keywords
                "store", "remember", "track", "save", "history", "previous", "findings", "knowledge",
                "memory", "record", "archive", "preserve", "maintain", "keep",
                # Chinese keywords
                "存储", "保存", "记录", "追踪", "跟踪", "历史", "之前", "发现", "知识", "记忆",
                "存档", "维护", "保持", "储存", "建立", "创建", "图谱", "实体", "关系"
            ],
            "priority": "high",
            "agents": ["researcher", "coder"]
        },
        
        # Search and information retrieval
        "search": {
            "keywords": [
                # English keywords
                "search", "find", "discover", "explore", "investigate", "research", "academic", "papers",
                "retrieve", "lookup", "query", "browse",
                # Chinese keywords
                "搜索", "查找", "发现", "探索", "调查", "研究", "学术", "论文", "检索", "查询",
                "浏览", "寻找", "获取", "收集"
            ],
            "priority": "high", 
            "agents": ["researcher"]
        },
        
        # Data analysis and processing
        "analysis": {
            "keywords": [
                # English keywords
                "analyze", "process", "calculate", "statistics", "data", "metrics", "trends", "patterns",
                "computation", "algorithm", "model", "evaluation",
                # Chinese keywords
                "分析", "处理", "计算", "统计", "数据", "指标", "趋势", "模式", "算法",
                "模型", "评估", "计算", "处理", "解析"
            ],
            "priority": "medium",
            "agents": ["researcher", "coder"]
        },
        
        # File and document management
        "filesystem": {
            "keywords": [
                # English keywords
                "file", "document", "read", "write", "csv", "json", "pdf", "text", "local",
                "folder", "directory", "path", "upload", "download",
                # Chinese keywords
                "文件", "文档", "读取", "写入", "本地", "目录", "路径", "上传", "下载",
                "文本", "资料", "材料"
            ],
            "priority": "medium",
            "agents": ["coder", "researcher"]
        },
        
        # Database operations
        "database": {
            "keywords": [
                # English keywords
                "database", "sql", "query", "table", "records", "store", "retrieve",
                "insert", "update", "delete", "select",
                # Chinese keywords
                "数据库", "查询", "表格", "记录", "插入", "更新", "删除", "选择"
            ],
            "priority": "medium",
            "agents": ["coder"]
        },
        
        # Web and API integration
        "web_api": {
            "keywords": [
                # English keywords
                "api", "web", "http", "rest", "service", "integration", "external",
                "endpoint", "request", "response",
                # Chinese keywords
                "接口", "网络", "服务", "集成", "外部", "请求", "响应", "调用"
            ],
            "priority": "low",
            "agents": ["coder", "researcher"]
        },
        
        # Citation and reference management
        "citation": {
            "keywords": [
                # English keywords
                "citation", "reference", "bibliography", "source", "academic", "paper",
                "cite", "bibliography", "footnote",
                # Chinese keywords
                "引用", "参考", "文献", "来源", "学术", "论文", "引文", "脚注", "参考文献"
            ],
            "priority": "medium",
            "agents": ["researcher"]
        },
        
        # Time and scheduling
        "temporal": {
            "keywords": [
                # English keywords
                "time", "date", "schedule", "timeline", "recent", "latest", "current",
                "when", "period", "duration",
                # Chinese keywords
                "时间", "日期", "时间表", "时间线", "最近", "最新", "当前", "何时", "期间", "持续"
            ],
            "priority": "low",
            "agents": ["researcher"]
        }
    }
    
    recommendations = {}
    
    for category, config in tool_patterns.items():
        if agent_type in config["agents"]:
            # Check if any keywords match the content
            keyword_matches = sum(1 for keyword in config["keywords"] if keyword in content)
            if keyword_matches > 0:
                recommendations[category] = {
                    "priority": config["priority"],
                    "match_score": keyword_matches,
                    "keywords_found": [kw for kw in config["keywords"] if kw in content]
                }
    
    return recommendations


def _enhance_tool_descriptions_with_context(tools: list, step_title: str, step_description: str, recommendations: dict) -> list:
    """
    Enhance tool descriptions with context-specific guidance based on the current research step.
    
    Args:
        tools: List of available tools
        step_title: Current step title
        step_description: Current step description
        recommendations: Tool recommendations from intelligent analysis
    
    Returns:
        List of tools with enhanced descriptions
    """
    enhanced_tools = []
    
    for tool in tools:
        enhanced_tool = tool
        tool_name = tool.name.lower()
        
        # Add context-specific guidance to tool descriptions
        context_guidance = ""
        
        # Memory tools guidance
        if any(keyword in tool_name for keyword in ["memory", "store", "save"]) and "memory" in recommendations:
            context_guidance = f"\n🎯 RECOMMENDED for this step: Store key findings about '{step_title}' for later reference and cross-step analysis."
        
        # Search tools guidance  
        elif any(keyword in tool_name for keyword in ["search", "web", "brave"]) and "search" in recommendations:
            context_guidance = f"\n🎯 RECOMMENDED for this step: Use for comprehensive research on '{step_title}' topics."
        
        # File system tools guidance
        elif any(keyword in tool_name for keyword in ["file", "read", "write"]) and "filesystem" in recommendations:
            context_guidance = f"\n🎯 RECOMMENDED for this step: Access local files or documents related to '{step_title}'."
        
        # Analysis tools guidance
        elif any(keyword in tool_name for keyword in ["analyze", "process", "data"]) and "analysis" in recommendations:
            context_guidance = f"\n🎯 RECOMMENDED for this step: Process and analyze data for '{step_title}' insights."
        
        # Citation tools guidance
        elif any(keyword in tool_name for keyword in ["citation", "reference", "bib"]) and "citation" in recommendations:
            context_guidance = f"\n🎯 RECOMMENDED for this step: Manage references and citations for '{step_title}' research."
        
        if context_guidance:
            enhanced_tool.description = f"{tool.description}{context_guidance}"
        
        enhanced_tools.append(enhanced_tool)
    
    return enhanced_tools


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type (and intelligent recommendations)
    2. Creates an agent with the appropriate tools.
    3. Executes the agent on the current step.

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    import asyncio # Ensure asyncio is imported

    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    observations = state.get("observations", []) # Get observations at the beginning

    # Get current step for intelligent tool selection and execution
    # This is the step that will be executed by the agent
    current_step_to_execute = None
    completed_steps_for_input = [] # For providing context to the agent
    if current_plan and current_plan.steps:
        for step_obj in current_plan.steps:
            if not step_obj.execution_res:
                current_step_to_execute = step_obj
                break # Found the step to execute
            else:
                completed_steps_for_input.append(step_obj)
    
    if not current_step_to_execute:
        logger.warning(f"No unexecuted step found for {agent_type}. Returning to research_team.")
        return Command(goto="research_team")

    # Get intelligent tool recommendations
    recommendations = {}
    recommendations = _get_intelligent_tool_recommendations(
        current_step_to_execute.title, 
        current_step_to_execute.description, 
        agent_type
    )
    logger.info(f"🧠 Intelligent tool recommendations for {agent_type} on step '{current_step_to_execute.title}': {recommendations}")
    
    mcp_servers_config = {} # Renamed to avoid confusion with mcp_servers local var in original
    enabled_mcp_tools = {} # Renamed

    if configurable.mcp_settings:
        for server_name, server_config_item in configurable.mcp_settings["servers"].items(): # Renamed server_config
            should_add_server = False
            # ... (Existing logic for should_add_server based on recommendations and explicit config)
            # This logic (lines 816-896 approx) remains the same.
            # For brevity in this diff, I'm assuming it's correctly placed here.
            # --- Start of existing server selection logic ---
            if (server_config_item.get("enabled_tools") and 
                agent_type in server_config_item.get("add_to_agents", [])):
                if recommendations:
                    server_tools = server_config_item.get("enabled_tools", [])
                    is_relevant = False
                    for tool_name in server_tools:
                        tool_name_lower = tool_name.lower()
                        if ("memory" in recommendations and any(keyword in tool_name_lower for keyword in ["memory", "entities", "relations", "observations", "store", "save", "create", "add"])) or \
                           ("search" in recommendations and any(keyword in tool_name_lower for keyword in ["search", "find", "query", "retrieve", "browse", "papers", "paper"])) or \
                           ("filesystem" in recommendations and any(keyword in tool_name_lower for keyword in ["file", "read", "write", "directory", "path"])) or \
                           ("analysis" in recommendations and any(keyword in tool_name_lower for keyword in ["analyze", "process", "calculate", "data", "statistics"])) or \
                           ("citation" in recommendations and any(keyword in tool_name_lower for keyword in ["citation", "reference", "bibliography", "cite"])):
                            is_relevant = True
                            break
                    if is_relevant: should_add_server = True; logger.info(f"📋✨ Explicitly configured server '{server_name}' for {agent_type} - RELEVANT to current task")
                    else: logger.info(f"📋⏭️ Skipping explicitly configured server '{server_name}' for {agent_type} - NOT relevant to current task")
                else: should_add_server = True; logger.info(f"📋 Explicitly configured server '{server_name}' for {agent_type}")
            elif server_config_item.get("enabled_tools") and recommendations and not server_config_item.get("add_to_agents"):
                server_tools = server_config_item.get("enabled_tools", [])
                for tool_name in server_tools:
                    tool_name_lower = tool_name.lower()
                    if ("memory" in recommendations and any(keyword in tool_name_lower for keyword in ["memory", "entities", "relations", "observations", "store", "save", "create", "add"])): should_add_server = True; logger.info(f"🎯 Auto-enabling server '{server_name}' for {agent_type} based on memory tool recommendation"); break
                    elif ("search" in recommendations and any(keyword in tool_name_lower for keyword in ["search", "find", "query", "retrieve", "browse", "papers", "paper"])): should_add_server = True; logger.info(f"🎯 Auto-enabling server '{server_name}' for {agent_type} based on search tool recommendation"); break
                    elif ("filesystem" in recommendations and any(keyword in tool_name_lower for keyword in ["file", "read", "write", "directory", "path"])): should_add_server = True; logger.info(f"🎯 Auto-enabling server '{server_name}' for {agent_type} based on filesystem tool recommendation"); break
                    elif ("analysis" in recommendations and any(keyword in tool_name_lower for keyword in ["analyze", "process", "calculate", "data", "statistics"])): should_add_server = True; logger.info(f"🎯 Auto-enabling server '{server_name}' for {agent_type} based on analysis tool recommendation"); break
                    elif ("citation" in recommendations and any(keyword in tool_name_lower for keyword in ["citation", "reference", "bibliography", "cite"])): should_add_server = True; logger.info(f"🎯 Auto-enabling server '{server_name}' for {agent_type} based on citation tool recommendation"); break
            # --- End of existing server selection logic ---
            if should_add_server:
                mcp_servers_config[server_name] = {
                    k: v
                    for k, v in server_config_item.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config_item["enabled_tools"]:
                    enabled_mcp_tools[tool_name] = server_name

    # Agent execution logic, adapted from the original _execute_agent_step
    async def _invoke_agent_on_step(agent_instance, step_to_run, completed_steps_context):
        logger.info(f"Executing step: {step_to_run.title} with agent {agent_type}")
        
        completed_steps_info_str = ""
        if completed_steps_context:
            completed_steps_info_str = "# Existing Research Findings\\n\\n"
            for i, c_step in enumerate(completed_steps_context):
                completed_steps_info_str += f"## Existing Finding {i+1}: {c_step.title}\\n\\n"
                completed_steps_info_str += f"<finding>\\n{c_step.execution_res}\\n</finding>\\n\\n"

        agent_input_dict = {
            "messages": [
                HumanMessage(
                    content=f"{completed_steps_info_str}# Current Task\\n\\n## Title\\n\\n{step_to_run.title}\\n\\n## Description\\n\\n{step_to_run.description}\\n\\n## Locale\\n\\n{state.get('locale', 'en-US')}"
                )
            ]
        }
        if agent_type == "researcher":
            agent_input_dict["messages"].append(
                HumanMessage(
                    content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\\n- [Source Title](URL)\\n\\n- [Another Source](URL)",
                    name="system",
                )
            )
        
        default_recursion_limit = 25
        recursion_limit = default_recursion_limit
        try:
            env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
            parsed_limit = int(env_value_str)
            if parsed_limit > 0: recursion_limit = parsed_limit
            else: logger.warning(f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. Using default {default_recursion_limit}.")
        except ValueError: logger.warning(f"Invalid AGENT_RECURSION_LIMIT value: '{os.getenv('AGENT_RECURSION_LIMIT')}'. Using default {default_recursion_limit}.")

        logger.info(f"[DEBUG] Invoking agent '{agent_type}' with input: {agent_input_dict}")
        result = await agent_instance.ainvoke(input=agent_input_dict, config={"recursion_limit": recursion_limit})
        logger.info(f"[DEBUG] Agent '{agent_type}' raw result: {result}")

        response_content = result["messages"][-1].content
        logger.debug(f"{agent_type.capitalize()} full response: {response_content}") # 恢复此行日志
        step_to_run.execution_res = response_content # Update the original step object
        logger.info(f"Step '{step_to_run.title}' execution completed by {agent_type}")

        return Command(
            update={
                "messages": [HumanMessage(content=response_content, name=agent_type)],
                "observations": observations + [response_content], # Use observations from outer scope
            },
            goto="research_team",
        )

    # Create and execute agent
    if mcp_servers_config:
        try:
            logger.info(f"🔌 Attempting to connect to {len(mcp_servers_config)} MCP server(s): {list(mcp_servers_config.keys())}")
            # Correctly manage MultiServerMCPClient lifecycle
            # Timeout can wrap the 'async with' if using asyncio.timeout (Python 3.11+)
            # For now, focusing on ClosedResourceError by correct 'async with' usage
            async with MultiServerMCPClient(mcp_servers_config) as client:
                logger.info("✅ MCP servers connected successfully (client context entered)")
                
                loaded_mcp_tools = default_tools[:] # Start with default tools
                actual_mcp_tools_loaded = [] # For logging
                
                for tool_instance in client.get_tools():
                    if tool_instance.name in enabled_mcp_tools:
                        tool_instance.description = (
                            f"Powered by '{enabled_mcp_tools[tool_instance.name]}'.\\n{tool_instance.description}"
                        )
                        actual_mcp_tools_loaded.append(tool_instance)
                
                if current_step_to_execute and actual_mcp_tools_loaded:
                    actual_mcp_tools_loaded = _enhance_tool_descriptions_with_context(
                        actual_mcp_tools_loaded, 
                        current_step_to_execute.title, 
                        current_step_to_execute.description, 
                        recommendations
                    )
                
                loaded_mcp_tools.extend(actual_mcp_tools_loaded)
                
                if actual_mcp_tools_loaded:
                    tool_names = [t.name for t in actual_mcp_tools_loaded]
                    logger.info(f"🔧 Enhanced {agent_type} with {len(actual_mcp_tools_loaded)} MCP tools: {tool_names}")
                
                mcp_agent = create_agent(agent_type, agent_type, loaded_mcp_tools, agent_type)
                return await _invoke_agent_on_step(mcp_agent, current_step_to_execute, completed_steps_for_input)
                
        except asyncio.TimeoutError: # If a timeout wraps the above block and triggers
            logger.warning("⏰ MCP server operation timed out.")
            logger.info("🔄 Falling back to default tools")
            # Fallback: create agent with default tools and execute
            default_agent = create_agent(agent_type, agent_type, default_tools, agent_type)
            return await _invoke_agent_on_step(default_agent, current_step_to_execute, completed_steps_for_input)
        except Exception as e:
            logger.warning(f"❌ Failed to start or use MCP servers: {e}. Using default tools instead.")
            # Fallback: create agent with default tools and execute
            default_agent_on_error = create_agent(agent_type, agent_type, default_tools, agent_type)
            return await _invoke_agent_on_step(default_agent_on_error, current_step_to_execute, completed_steps_for_input)
    else:
        # Use default tools if no MCP servers are configured
        logger.info(f"🛠️ Using default tools for {agent_type} (no MCP servers configured or recommended)")
        vanilla_agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _invoke_agent_on_step(vanilla_agent, current_step_to_execute, completed_steps_for_input)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        [get_web_search_tool(configurable.max_search_results), crawl_tool],
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )
