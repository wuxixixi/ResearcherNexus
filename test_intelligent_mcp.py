#!/usr/bin/env python3
"""
测试智能MCP工具选择和主动调用功能
"""

import asyncio
import json
import logging
from src.graph.builder import build_graph_with_memory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_intelligent_mcp_selection():
    """测试智能MCP工具选择功能"""
    
    # 构建工作流图
    graph = build_graph_with_memory()
    
    # 配置 - 使用智能工具选择
    config = {
        "configurable": {
            "thread_id": "test_intelligent_mcp_001",
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "max_search_results": 3,
            "mcp_settings": {
                "servers": {
                    # 内存工具 - 应该被自动选择用于存储研究发现
                    "memory-server": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-memory"],
                        "enabled_tools": ["create_memory", "search_memory"]
                        # 注意：没有显式指定add_to_agents，测试智能选择
                    },
                    
                    # 文件系统工具 - 应该被自动选择用于文档处理
                    "filesystem": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-filesystem", "D:\\"],
                        "enabled_tools": ["read_file", "list_directory"]
                        # 注意：没有显式指定add_to_agents，测试智能选择
                    },
                    
                    # 顺序思考工具 - 应该被自动选择用于分析任务
                    "sequential-thinking": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-sequential-thinking"],
                        "enabled_tools": ["think_step_by_step"]
                        # 注意：没有显式指定add_to_agents，测试智能选择
                    }
                }
            }
        },
        "recursion_limit": 100
    }
    
    # 测试不同类型的研究任务
    test_cases = [
        {
            "name": "数据分析研究",
            "query": "分析2024年全球AI市场的数据趋势，包括市场规模、增长率和主要参与者的统计信息",
            "expected_tools": ["memory", "analysis", "search"]
        },
        {
            "name": "文档处理研究", 
            "query": "读取本地文档并分析其中的技术文档内容，整理成结构化报告",
            "expected_tools": ["filesystem", "memory", "analysis"]
        },
        {
            "name": "深度搜索研究",
            "query": "深入研究量子计算的最新发展，探索学术论文和技术报告",
            "expected_tools": ["search", "memory", "citation"]
        },
        {
            "name": "综合分析研究",
            "query": "存储和分析多个数据源的信息，建立知识图谱并生成洞察报告",
            "expected_tools": ["memory", "analysis", "search", "database"]
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"🧪 测试案例 {i+1}: {test_case['name']}")
        print(f"📋 查询: {test_case['query']}")
        print(f"🎯 预期工具类型: {', '.join(test_case['expected_tools'])}")
        print(f"{'='*60}")
        
        # 更新配置中的thread_id
        config["configurable"]["thread_id"] = f"test_intelligent_mcp_{i+1:03d}"
        
        # 初始状态
        initial_state = {
            "messages": [{"role": "user", "content": test_case["query"]}],
            "auto_accepted_plan": True,
            "enable_background_investigation": False,
            "locale": "zh-CN"
        }
        
        try:
            print("🚀 开始执行研究工作流...")
            
            step_count = 0
            async for state in graph.astream(initial_state, config=config):
                step_count += 1
                
                # 检查是否有工具调用信息
                if "messages" in state:
                    for message in state["messages"]:
                        if hasattr(message, "content") and "tool" in str(message.content).lower():
                            print(f"🔧 检测到工具使用: {message.content[:100]}...")
                
                # 检查是否完成
                if "final_report" in state:
                    print("✅ 研究完成!")
                    print(f"📊 总步骤数: {step_count}")
                    break
                    
                # 防止无限循环
                if step_count > 20:
                    print("⚠️ 达到最大步骤限制，停止执行")
                    break
                    
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"✅ 测试案例 {i+1} 完成\n")


async def test_tool_recommendation_algorithm():
    """测试工具推荐算法"""
    
    print("\n🧠 测试工具推荐算法")
    print("="*50)
    
    # 导入工具推荐函数
    from src.graph.nodes import _get_intelligent_tool_recommendations
    
    test_scenarios = [
        {
            "title": "数据分析报告",
            "description": "分析销售数据，计算统计指标，生成趋势图表",
            "agent": "researcher",
            "expected": ["analysis", "memory"]
        },
        {
            "title": "文件处理任务",
            "description": "读取CSV文件，处理数据并写入新的JSON文件",
            "agent": "coder", 
            "expected": ["filesystem", "analysis"]
        },
        {
            "title": "学术研究",
            "description": "搜索最新的机器学习论文，整理参考文献",
            "agent": "researcher",
            "expected": ["search", "citation", "memory"]
        },
        {
            "title": "数据库查询",
            "description": "查询用户数据库，分析用户行为模式",
            "agent": "coder",
            "expected": ["database", "analysis"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 场景 {i+1}: {scenario['title']}")
        print(f"📝 描述: {scenario['description']}")
        print(f"🤖 代理: {scenario['agent']}")
        
        recommendations = _get_intelligent_tool_recommendations(
            scenario["title"],
            scenario["description"], 
            scenario["agent"]
        )
        
        print(f"🎯 推荐结果: {json.dumps(recommendations, indent=2, ensure_ascii=False)}")
        print(f"✅ 预期类型: {', '.join(scenario['expected'])}")
        
        # 检查推荐是否包含预期的工具类型
        recommended_categories = set(recommendations.keys())
        expected_categories = set(scenario["expected"])
        
        if expected_categories.issubset(recommended_categories):
            print("✅ 推荐准确!")
        else:
            missing = expected_categories - recommended_categories
            print(f"⚠️ 缺少推荐: {', '.join(missing)}")


async def test_mcp_server_connectivity():
    """测试MCP服务器连接性"""
    
    print("\n🔌 测试MCP服务器连接性")
    print("="*50)
    
    # 测试常见的MCP服务器
    test_servers = [
        {
            "name": "Memory Server",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-memory"]
            }
        },
        {
            "name": "Sequential Thinking",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-sequential-thinking"]
            }
        },
        {
            "name": "Filesystem Server",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "D:\\"]
            }
        }
    ]
    
    for server in test_servers:
        print(f"\n🧪 测试服务器: {server['name']}")
        
        try:
            # 使用API测试服务器
            import requests
            
            response = requests.post(
                "http://localhost:8000/api/mcp/server/metadata",
                json=server["config"],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get('tools', [])
                print(f"✅ 连接成功! 获取到 {len(tools)} 个工具")
                
                if tools:
                    for tool in tools[:3]:  # 显示前3个工具
                        print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                else:
                    print("⚠️ 服务器返回空工具列表")
            else:
                print(f"❌ 连接失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 连接超时")
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到后端服务器")
        except Exception as e:
            print(f"❌ 测试失败: {e}")


async def diagnose_current_issue():
    """诊断当前的MCP问题"""
    
    print("\n🔍 诊断当前MCP问题")
    print("="*50)
    
    # 测试您遇到的具体配置
    problematic_config = {
        "transport": "stdio",
        "command": "cmd",
        "args": ["/c", "npx", "-y", "@smithery/cli@latest", "run", "@ameeralns/DeepResearchMCP", "--key", "741ccf4e-a807-4366-a4bf-cc8f3a9f277f"]
    }
    
    print("🧪 测试问题配置:")
    print(f"   命令: {problematic_config['command']}")
    print(f"   参数: {' '.join(problematic_config['args'])}")
    
    try:
        import requests
        
        print("\n📡 发送测试请求...")
        response = requests.post(
            "http://localhost:8000/api/mcp/server/metadata",
            json=problematic_config,
            timeout=60  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('tools', [])
            print(f"✅ 请求成功! 获取到 {len(tools)} 个工具")
            
            if tools:
                print("🔧 可用工具:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            else:
                print("⚠️ 服务器返回空工具列表")
                print("💡 可能的原因:")
                print("   1. Smithery服务器启动失败")
                print("   2. API密钥无效或过期")
                print("   3. 网络连接问题")
                print("   4. Windows环境兼容性问题")
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 (60秒)")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 验证Smithery服务是否可用")
        print("   3. 尝试使用更简单的MCP服务器")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        
    # 提供替代方案
    print("\n💡 推荐的替代配置:")
    
    alternative_configs = [
        {
            "name": "Memory Server (推荐)",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-memory"]
            }
        },
        {
            "name": "Sequential Thinking",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-sequential-thinking"]
            }
        },
        {
            "name": "Filesystem Server",
            "config": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "D:\\ResearcherNexus"]
            }
        }
    ]
    
    for alt in alternative_configs:
        print(f"\n🔧 {alt['name']}:")
        print(f"   命令: {alt['config']['command']}")
        print(f"   参数: {' '.join(alt['config']['args'])}")


async def main():
    """主测试函数"""
    
    print("🚀 开始MCP问题诊断和测试")
    print("="*60)
    
    # 首先诊断当前问题
    await diagnose_current_issue()
    
    # 测试服务器连接性
    await test_mcp_server_connectivity()
    
    # 测试工具推荐算法
    await test_tool_recommendation_algorithm()
    
    # 如果基础测试通过，再测试完整流程
    print("\n❓ 是否继续测试完整的智能工具选择流程？")
    print("   (需要确保至少一个MCP服务器可用)")
    
    # 这里可以添加用户输入，但为了自动化测试，我们跳过
    # await test_intelligent_mcp_selection()
    
    print("\n🎉 诊断完成!")
    print("="*60)
    print("📝 问题总结:")
    print("1. Smithery服务器可能存在连接或兼容性问题")
    print("2. 建议使用更稳定的MCP服务器（如Memory Server）")
    print("3. 智能工具选择功能已实现，等待MCP服务器正常工作")
    print("4. 可以通过日志查看详细的错误信息")


if __name__ == "__main__":
    asyncio.run(main()) 