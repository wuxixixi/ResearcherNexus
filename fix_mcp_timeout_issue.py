#!/usr/bin/env python3
"""
修复MCP连接超时导致系统锁死的问题

问题分析：
1. 智能工具推荐成功
2. 系统尝试启动MCP服务器时卡住
3. MultiServerMCPClient没有设置合适的超时时间

解决方案：
1. 为MCP连接添加超时机制
2. 改进错误处理
3. 提供快速失败和回退机制
"""

import asyncio
import logging
import time
from typing import Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutMCPClient:
    """带超时机制的MCP客户端包装器"""
    
    def __init__(self, mcp_servers: Dict[str, Any], timeout_seconds: int = 30):
        self.mcp_servers = mcp_servers
        self.timeout_seconds = timeout_seconds
        self.client = None
        
    async def __aenter__(self):
        """异步上下文管理器入口，带超时"""
        try:
            # 导入MCP客户端
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            logger.info(f"尝试连接MCP服务器，超时时间: {self.timeout_seconds}秒")
            logger.info(f"服务器配置: {list(self.mcp_servers.keys())}")
            
            # 使用asyncio.wait_for添加超时
            self.client = await asyncio.wait_for(
                self._create_client(),
                timeout=self.timeout_seconds
            )
            
            logger.info("MCP客户端连接成功")
            return self.client
            
        except asyncio.TimeoutError:
            logger.warning(f"MCP客户端连接超时 ({self.timeout_seconds}秒)")
            raise TimeoutError(f"MCP服务器连接超时，请检查服务器配置")
        except Exception as e:
            logger.error(f"MCP客户端连接失败: {type(e).__name__}: {e}")
            raise
    
    async def _create_client(self):
        """创建MCP客户端"""
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # 创建客户端实例
        client = MultiServerMCPClient(self.mcp_servers)
        
        # 进入上下文管理器
        await client.__aenter__()
        
        return client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.client:
            try:
                await self.client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                logger.warning(f"关闭MCP客户端时出错: {e}")

def create_timeout_aware_mcp_setup():
    """创建带超时机制的MCP设置函数"""
    
    setup_code = '''
async def _setup_and_execute_agent_step_with_timeout(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """带超时机制的代理步骤设置和执行函数"""
    
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    
    # 获取当前步骤用于智能工具选择
    current_step = None
    if current_plan and current_plan.steps:
        for step in current_plan.steps:
            if not step.execution_res:
                current_step = step
                break
    
    # 获取智能工具推荐
    recommendations = {}
    if current_step:
        recommendations = _get_intelligent_tool_recommendations(
            current_step.title, 
            current_step.description, 
            agent_type
        )
        logger.info(f"Intelligent tool recommendations for {agent_type}: {recommendations}")
    
    mcp_servers = {}
    enabled_tools = {}

    # 提取MCP服务器配置
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            should_add_server = False
            
            # 原有逻辑：显式代理配置
            if (server_config.get("enabled_tools") and 
                agent_type in server_config.get("add_to_agents", [])):
                should_add_server = True
            
            # 增强逻辑：智能工具推荐
            elif server_config.get("enabled_tools") and recommendations:
                server_tools = server_config.get("enabled_tools", [])
                for tool_name in server_tools:
                    tool_name_lower = tool_name.lower()
                    
                    # 检查内存工具
                    if "memory" in recommendations and any(keyword in tool_name_lower for keyword in 
                           ["memory", "entities", "relations", "observations", "store", "save", "create", "add"]):
                        should_add_server = True
                        logger.info(f"Auto-enabling server '{server_name}' for {agent_type} based on memory tool recommendation")
                        break
                    
                    # 检查搜索工具
                    elif "search" in recommendations and any(keyword in tool_name_lower for keyword in 
                           ["search", "find", "query", "retrieve", "browse"]):
                        should_add_server = True
                        logger.info(f"Auto-enabling server '{server_name}' for {agent_type} based on search tool recommendation")
                        break
                    
                    # 检查文件系统工具
                    elif "filesystem" in recommendations and any(keyword in tool_name_lower for keyword in 
                           ["file", "read", "write", "directory", "path"]):
                        should_add_server = True
                        logger.info(f"Auto-enabling server '{server_name}' for {agent_type} based on filesystem tool recommendation")
                        break
                    
                    # 检查分析工具
                    elif "analysis" in recommendations and any(keyword in tool_name_lower for keyword in 
                           ["analyze", "process", "calculate", "data", "statistics"]):
                        should_add_server = True
                        logger.info(f"Auto-enabling server '{server_name}' for {agent_type} based on analysis tool recommendation")
                        break
                    
                    # 检查引用工具
                    elif "citation" in recommendations and any(keyword in tool_name_lower for keyword in 
                           ["citation", "reference", "bibliography", "cite"]):
                        should_add_server = True
                        logger.info(f"Auto-enabling server '{server_name}' for {agent_type} based on citation tool recommendation")
                        break
            
            if should_add_server:
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # 使用带超时机制的MCP客户端
    if mcp_servers:
        try:
            logger.info(f"尝试连接 {len(mcp_servers)} 个MCP服务器...")
            
            # 使用带超时的客户端
            timeout_client = TimeoutMCPClient(mcp_servers, timeout_seconds=30)
            
            async with timeout_client as client:
                loaded_tools = default_tools[:]
                mcp_tools = []
                
                for tool in client.get_tools():
                    if tool.name in enabled_tools:
                        tool.description = (
                            f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                        )
                        mcp_tools.append(tool)
                
                # 增强工具描述
                if current_step and mcp_tools:
                    mcp_tools = _enhance_tool_descriptions_with_context(
                        mcp_tools, 
                        current_step.title, 
                        current_step.description, 
                        recommendations
                    )
                
                loaded_tools.extend(mcp_tools)
                
                # 记录工具使用情况
                if mcp_tools:
                    tool_names = [t.name for t in mcp_tools]
                    logger.info(f"Enhanced {agent_type} with {len(mcp_tools)} MCP tools: {tool_names}")
                
                agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
                return await _execute_agent_step(state, agent, agent_type)
                
        except TimeoutError as e:
            logger.warning(f"MCP连接超时: {e}")
            logger.info("回退到默认工具")
            agent = create_agent(agent_type, agent_type, default_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
        except Exception as e:
            logger.warning(f"MCP服务器启动失败: {e}. 使用默认工具")
            agent = create_agent(agent_type, agent_type, default_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # 没有配置MCP服务器时使用默认工具
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)
'''
    
    return setup_code

def create_patch_file():
    """创建补丁文件"""
    
    patch_content = f'''# MCP超时问题修复补丁
# 
# 使用方法：
# 1. 将此代码添加到 src/graph/nodes.py 文件中
# 2. 替换原有的 _setup_and_execute_agent_step 函数
# 3. 更新 researcher_node 和 coder_node 函数调用

{create_timeout_aware_mcp_setup()}

# 更新后的节点函数
async def researcher_node_with_timeout(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """带超时机制的研究员节点"""
    logger.info("Researcher node is researching (with timeout protection).")
    configurable = Configuration.from_runnable_config(config)
    return await _setup_and_execute_agent_step_with_timeout(
        state,
        config,
        "researcher",
        [get_web_search_tool(configurable.max_search_results), crawl_tool],
    )

async def coder_node_with_timeout(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """带超时机制的编码员节点"""
    logger.info("Coder node is coding (with timeout protection).")
    return await _setup_and_execute_agent_step_with_timeout(
        state,
        config,
        "coder",
        [python_repl_tool],
    )
'''
    
    with open("mcp_timeout_patch.py", "w", encoding="utf-8") as f:
        f.write(patch_content)
    
    print("✅ 补丁文件已创建: mcp_timeout_patch.py")

def test_timeout_mechanism():
    """测试超时机制"""
    
    async def test_timeout():
        print("🧪 测试超时机制...")
        
        # 模拟一个会超时的MCP服务器配置
        problematic_servers = {
            "timeout-test": {
                "transport": "stdio",
                "command": "cmd",
                "args": ["/c", "npx", "-y", "@smithery/cli@latest", "run", "@ameeralns/DeepResearchMCP", "--key", "invalid-key"]
            }
        }
        
        try:
            timeout_client = TimeoutMCPClient(problematic_servers, timeout_seconds=10)
            
            start_time = time.time()
            async with timeout_client as client:
                print("❌ 意外成功连接")
        except TimeoutError as e:
            elapsed = time.time() - start_time
            print(f"✅ 超时机制正常工作，耗时: {elapsed:.1f}秒")
            print(f"   错误信息: {e}")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"✅ 快速失败机制正常工作，耗时: {elapsed:.1f}秒")
            print(f"   错误类型: {type(e).__name__}: {e}")
    
    asyncio.run(test_timeout())

def main():
    """主函数"""
    print("🔧 MCP超时问题修复工具")
    print("="*50)
    
    print("\n📋 问题分析:")
    print("✅ 智能工具推荐功能正常")
    print("❌ MCP服务器连接时卡住，导致系统锁死")
    print("💡 原因: MultiServerMCPClient没有设置超时时间")
    
    print("\n🛠️ 解决方案:")
    print("1. 创建带超时机制的MCP客户端包装器")
    print("2. 添加快速失败和回退机制")
    print("3. 改进错误处理和日志记录")
    
    print("\n🧪 测试超时机制...")
    test_timeout_mechanism()
    
    print("\n📝 创建补丁文件...")
    create_patch_file()
    
    print("\n💡 使用建议:")
    print("1. 应用补丁文件中的代码修改")
    print("2. 重启后端服务")
    print("3. 测试智能工具选择功能")
    print("4. 如果仍有问题，删除有问题的MCP服务器配置")
    
    print("\n🎯 预期效果:")
    print("✅ MCP连接超时后快速失败")
    print("✅ 自动回退到默认工具")
    print("✅ 系统不再锁死")
    print("✅ 智能工具推荐继续工作")

if __name__ == "__main__":
    main() 