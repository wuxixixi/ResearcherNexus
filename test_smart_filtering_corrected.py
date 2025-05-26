#!/usr/bin/env python3
"""
修正的智能过滤功能测试

使用更合适的测试场景来验证智能过滤功能
"""

import asyncio
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_smart_filtering_corrected():
    """测试智能过滤功能 - 修正版"""
    
    print("🧪 修正的智能过滤功能测试")
    print("="*60)
    
    try:
        from src.graph.nodes import _get_intelligent_tool_recommendations
        from src.config.configuration import Configuration
        from langchain_core.runnables import RunnableConfig
        
        # 测试场景1：文件处理任务
        print("\n1️⃣ 测试场景1：文件处理和数据分析任务")
        
        test_config_1 = {
            "configurable": {
                "thread_id": "file_processing_test",
                "mcp_settings": {
                    "servers": {
                        # 相关服务器：文件系统
                        "filesystem": {
                            "transport": "stdio",
                            "command": "npx",
                            "args": ["@modelcontextprotocol/server-filesystem", "D:\\"],
                            "enabled_tools": ["read_file", "write_file", "list_directory"],
                            "add_to_agents": ["researcher"]
                        },
                        # 不相关服务器：内存管理（对于文件处理不是必需的）
                        "memory-server": {
                            "transport": "stdio",
                            "command": "npx",
                            "args": ["@modelcontextprotocol/server-memory"],
                            "enabled_tools": ["create_entities", "create_relations"],
                            "add_to_agents": ["researcher"]
                        },
                        # 不相关服务器：论文搜索
                        "arxiv-paper-mcp": {
                            "transport": "stdio", 
                            "command": "cmd",
                            "args": ["/c", "npx", "-y", "@daheepk/arxiv-paper-mcp"],
                            "enabled_tools": ["search_papers", "get_paper_details"],
                            "add_to_agents": ["researcher"]
                        }
                    }
                }
            }
        }
        
        # 测试文件处理任务的推荐
        recommendations_1 = _get_intelligent_tool_recommendations(
            "本地文件数据分析",
            "读取CSV文件，处理数据，写入分析结果到本地文件", 
            "researcher"
        )
        
        print(f"📋 任务: 本地文件数据分析")
        print(f"✅ 智能推荐: {recommendations_1}")
        
        # 模拟过滤逻辑
        configurable_1 = Configuration.from_runnable_config(RunnableConfig(configurable=test_config_1["configurable"]))
        
        selected_servers_1 = []
        skipped_servers_1 = []
        
        for server_name, server_config in configurable_1.mcp_settings["servers"].items():
            if (server_config.get("enabled_tools") and 
                "researcher" in server_config.get("add_to_agents", [])):
                
                if recommendations_1:
                    server_tools = server_config.get("enabled_tools", [])
                    is_relevant = False
                    
                    for tool_name in server_tools:
                        tool_name_lower = tool_name.lower()
                        
                        if ("memory" in recommendations_1 and any(keyword in tool_name_lower for keyword in 
                               ["memory", "entities", "relations", "observations", "store", "save", "create", "add"])) or \
                           ("search" in recommendations_1 and any(keyword in tool_name_lower for keyword in 
                               ["search", "find", "query", "retrieve", "browse", "papers", "paper"])) or \
                           ("filesystem" in recommendations_1 and any(keyword in tool_name_lower for keyword in 
                               ["file", "read", "write", "directory", "path", "list"])) or \
                           ("analysis" in recommendations_1 and any(keyword in tool_name_lower for keyword in 
                               ["analyze", "process", "calculate", "data", "statistics"])):
                            is_relevant = True
                            break
                    
                    if is_relevant:
                        selected_servers_1.append(server_name)
                        print(f"📋✨ 选择服务器 '{server_name}' - 与文件处理任务相关")
                    else:
                        skipped_servers_1.append(server_name)
                        print(f"📋⏭️ 跳过服务器 '{server_name}' - 与文件处理任务不相关")
        
        print(f"结果: 选择 {selected_servers_1}, 跳过 {skipped_servers_1}")
        
        # 测试场景2：知识图谱构建任务
        print("\n2️⃣ 测试场景2：知识图谱构建任务")
        
        recommendations_2 = _get_intelligent_tool_recommendations(
            "构建知识图谱",
            "创建实体关系，存储知识结构，建立语义网络", 
            "researcher"
        )
        
        print(f"📋 任务: 构建知识图谱")
        print(f"✅ 智能推荐: {recommendations_2}")
        
        selected_servers_2 = []
        skipped_servers_2 = []
        
        # 使用相同的服务器配置测试
        for server_name, server_config in configurable_1.mcp_settings["servers"].items():
            if (server_config.get("enabled_tools") and 
                "researcher" in server_config.get("add_to_agents", [])):
                
                if recommendations_2:
                    server_tools = server_config.get("enabled_tools", [])
                    is_relevant = False
                    
                    for tool_name in server_tools:
                        tool_name_lower = tool_name.lower()
                        
                        if ("memory" in recommendations_2 and any(keyword in tool_name_lower for keyword in 
                               ["memory", "entities", "relations", "observations", "store", "save", "create", "add"])) or \
                           ("search" in recommendations_2 and any(keyword in tool_name_lower for keyword in 
                               ["search", "find", "query", "retrieve", "browse", "papers", "paper"])) or \
                           ("filesystem" in recommendations_2 and any(keyword in tool_name_lower for keyword in 
                               ["file", "read", "write", "directory", "path", "list"])) or \
                           ("analysis" in recommendations_2 and any(keyword in tool_name_lower for keyword in 
                               ["analyze", "process", "calculate", "data", "statistics"])):
                            is_relevant = True
                            break
                    
                    if is_relevant:
                        selected_servers_2.append(server_name)
                        print(f"📋✨ 选择服务器 '{server_name}' - 与知识图谱任务相关")
                    else:
                        skipped_servers_2.append(server_name)
                        print(f"📋⏭️ 跳过服务器 '{server_name}' - 与知识图谱任务不相关")
        
        print(f"结果: 选择 {selected_servers_2}, 跳过 {skipped_servers_2}")
        
        # 验证结果
        print("\n📊 测试验证:")
        print("="*40)
        
        # 场景1验证：文件处理任务应该选择filesystem，跳过其他
        scenario1_success = (
            "filesystem" in selected_servers_1 and 
            "memory-server" in skipped_servers_1 and
            "arxiv-paper-mcp" in skipped_servers_1
        )
        
        # 场景2验证：知识图谱任务应该选择memory-server，可能选择search
        scenario2_success = (
            "memory-server" in selected_servers_2 and
            "filesystem" in skipped_servers_2
        )
        
        if scenario1_success:
            print("✅ 场景1 (文件处理): 智能过滤正确")
        else:
            print("❌ 场景1 (文件处理): 智能过滤有误")
            
        if scenario2_success:
            print("✅ 场景2 (知识图谱): 智能过滤正确")
        else:
            print("❌ 场景2 (知识图谱): 智能过滤有误")
        
        if scenario1_success and scenario2_success:
            print("\n🎉 智能过滤功能工作正常！")
        else:
            print("\n⚠️ 智能过滤功能需要进一步调整")
            
    except Exception as e:
        print(f"❌ 测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🔧 修正的智能过滤功能测试")
    print("="*60)
    
    print("\n📋 测试目标:")
    print("✅ 验证文件处理任务选择filesystem工具")
    print("✅ 验证知识图谱任务选择memory工具")
    print("✅ 验证不相关工具被正确跳过")
    
    print("\n🚀 开始测试...")
    
    # 运行测试
    asyncio.run(test_smart_filtering_corrected())
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    main() 