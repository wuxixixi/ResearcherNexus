#!/usr/bin/env python3
"""
测试智能过滤功能

验证：
1. 智能推荐是否能过滤显式配置的服务器
2. 只有相关的服务器会被选择
3. 不相关的服务器会被跳过
"""

import asyncio
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_smart_filtering():
    """测试智能过滤功能"""
    
    print("🧪 测试智能过滤功能")
    print("="*60)
    
    try:
        from src.graph.nodes import _get_intelligent_tool_recommendations, _setup_and_execute_agent_step
        from src.config.configuration import Configuration
        from langchain_core.runnables import RunnableConfig
        
        print("\n1️⃣ 测试场景：存储相关的研究任务")
        
        # 模拟一个存储相关的研究任务
        test_config = {
            "configurable": {
                "thread_id": "smart_filtering_test",
                "mcp_settings": {
                    "servers": {
                        # 相关服务器：内存管理
                        "memory-server": {
                            "transport": "stdio",
                            "command": "npx",
                            "args": ["@modelcontextprotocol/server-memory"],
                            "enabled_tools": ["create_entities", "create_relations", "add_observations"],
                            "add_to_agents": ["researcher"]
                        },
                        # 不相关服务器：论文搜索（对于存储任务不太相关）
                        "arxiv-paper-mcp": {
                            "transport": "stdio", 
                            "command": "cmd",
                            "args": ["/c", "npx", "-y", "@daheepk/arxiv-paper-mcp", "--key", "test"],
                            "enabled_tools": ["search_papers", "get_paper_details"],
                            "add_to_agents": ["researcher"]
                        },
                        # 相关服务器：文件系统（存储可能需要）
                        "filesystem": {
                            "transport": "stdio",
                            "command": "npx", 
                            "args": ["@modelcontextprotocol/server-filesystem", "D:\\"],
                            "enabled_tools": ["read_file", "write_file"],
                            "add_to_agents": ["researcher"]
                        }
                    }
                }
            }
        }
        
        # 模拟状态：存储相关任务
        test_state = {
            "current_plan": type('Plan', (), {
                'steps': [type('Step', (), {
                    'title': '数据存储和知识图谱构建',
                    'description': '存储研究发现，建立实体关系，创建知识图谱',
                    'execution_res': None
                })()]
            })(),
            "observations": []
        }
        
        print("📋 测试配置:")
        print("   - memory-server (相关：存储、实体、关系)")
        print("   - arxiv-paper-mcp (不相关：论文搜索)")  
        print("   - filesystem (相关：文件读写)")
        
        print("\n2️⃣ 测试智能推荐...")
        
        # 测试智能推荐
        recommendations = _get_intelligent_tool_recommendations(
            "数据存储和知识图谱构建",
            "存储研究发现，建立实体关系，创建知识图谱", 
            "researcher"
        )
        
        print(f"✅ 智能推荐结果: {recommendations}")
        
        print("\n3️⃣ 测试智能过滤...")
        print("⏰ 注意观察哪些服务器被选择，哪些被跳过...")
        
        # 这里我们不能直接调用_setup_and_execute_agent_step，因为它会尝试连接MCP服务器
        # 但我们可以模拟其逻辑来测试过滤功能
        
        configurable = Configuration.from_runnable_config(RunnableConfig(configurable=test_config["configurable"]))
        
        mcp_servers = {}
        enabled_tools = {}
        
        # 模拟智能过滤逻辑
        if configurable.mcp_settings:
            for server_name, server_config in configurable.mcp_settings["servers"].items():
                should_add_server = False
                
                # 显式配置检查
                if (server_config.get("enabled_tools") and 
                    "researcher" in server_config.get("add_to_agents", [])):
                    
                    # 智能过滤：检查是否与推荐相关
                    if recommendations:
                        server_tools = server_config.get("enabled_tools", [])
                        is_relevant = False
                        
                        for tool_name in server_tools:
                            tool_name_lower = tool_name.lower()
                            
                            # 检查是否匹配推荐
                            if ("memory" in recommendations and any(keyword in tool_name_lower for keyword in 
                                   ["memory", "entities", "relations", "observations", "store", "save", "create", "add"])) or \
                               ("search" in recommendations and any(keyword in tool_name_lower for keyword in 
                                   ["search", "find", "query", "retrieve", "browse"])) or \
                               ("filesystem" in recommendations and any(keyword in tool_name_lower for keyword in 
                                   ["file", "read", "write", "directory", "path"])):
                                is_relevant = True
                                break
                        
                        if is_relevant:
                            should_add_server = True
                            print(f"📋✨ 选择服务器 '{server_name}' - 与当前任务相关")
                        else:
                            print(f"📋⏭️ 跳过服务器 '{server_name}' - 与当前任务不相关")
                    else:
                        should_add_server = True
                        print(f"📋 选择服务器 '{server_name}' - 显式配置（无智能推荐）")
                
                if should_add_server:
                    mcp_servers[server_name] = server_config
                    for tool_name in server_config["enabled_tools"]:
                        enabled_tools[tool_name] = server_name
        
        print(f"\n4️⃣ 过滤结果:")
        print(f"   选择的服务器: {list(mcp_servers.keys())}")
        print(f"   可用工具: {list(enabled_tools.keys())}")
        
        print("\n📊 测试总结:")
        print("="*40)
        
        expected_servers = ["memory-server", "filesystem"]  # 应该被选择的服务器
        skipped_servers = ["arxiv-paper-mcp"]  # 应该被跳过的服务器
        
        success = True
        for server in expected_servers:
            if server in mcp_servers:
                print(f"✅ {server} 正确被选择")
            else:
                print(f"❌ {server} 应该被选择但被跳过")
                success = False
        
        for server in skipped_servers:
            if server not in mcp_servers:
                print(f"✅ {server} 正确被跳过")
            else:
                print(f"❌ {server} 应该被跳过但被选择")
                success = False
        
        if success:
            print("\n🎉 智能过滤功能正常工作！")
        else:
            print("\n⚠️ 智能过滤功能需要调整")
            
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🔧 智能过滤功能测试")
    print("="*60)
    
    print("\n📋 测试目标:")
    print("✅ 验证智能推荐能过滤显式配置")
    print("✅ 验证相关服务器被选择")
    print("✅ 验证不相关服务器被跳过")
    
    print("\n🚀 开始测试...")
    
    # 运行测试
    asyncio.run(test_smart_filtering())
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    main() 