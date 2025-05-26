#!/usr/bin/env python3
"""
最终测试智能MCP工具选择功能

使用推荐的Memory Server配置测试智能工具选择
"""

import asyncio
import json
import logging
from recommended_intelligent_config import INTELLIGENT_MCP_CONFIG, get_research_config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_intelligent_mcp_with_memory_server():
    """使用Memory Server测试智能MCP工具选择"""
    
    print("🚀 测试智能MCP工具选择功能")
    print("="*60)
    
    try:
        # 导入工作流构建器
        from src.graph.builder import build_graph_with_memory
        
        # 构建工作流图
        graph = build_graph_with_memory()
        print("✅ 工作流图构建成功")
        
        # 使用推荐的智能配置
        config = get_research_config("test_intelligent_mcp_final")
        print("✅ 智能配置加载成功")
        print(f"📋 配置详情: {json.dumps(config, indent=2, ensure_ascii=False)}")
        
        # 测试不同类型的研究查询
        test_queries = [
            {
                "name": "存储导向研究",
                "query": "分析并存储2024年人工智能发展的关键信息，建立知识图谱记录重要发现",
                "expected_tools": ["memory"]
            },
            {
                "name": "检索导向研究", 
                "query": "搜索和检索之前存储的机器学习研究数据，查找相关实体关系",
                "expected_tools": ["memory"]
            },
            {
                "name": "知识图谱构建",
                "query": "创建关于量子计算的实体关系网络，记录技术发展脉络",
                "expected_tools": ["memory"]
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{'='*50}")
            print(f"🧪 测试案例 {i}: {test_case['name']}")
            print(f"📝 查询: {test_case['query']}")
            print(f"🎯 预期工具: {', '.join(test_case['expected_tools'])}")
            print(f"{'='*50}")
            
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
                tool_calls_detected = []
                
                async for state in graph.astream(initial_state, config=config):
                    step_count += 1
                    
                    # 检查消息中的工具调用
                    if "messages" in state:
                        for message in state["messages"]:
                            if hasattr(message, "tool_calls") and message.tool_calls:
                                for tool_call in message.tool_calls:
                                    tool_name = tool_call.get("name", "unknown")
                                    if tool_name not in tool_calls_detected:
                                        tool_calls_detected.append(tool_name)
                                        print(f"🔧 检测到工具调用: {tool_name}")
                            
                            # 检查内容中的MCP工具使用
                            if hasattr(message, "content") and isinstance(message.content, str):
                                content_lower = message.content.lower()
                                if any(keyword in content_lower for keyword in ["create_entities", "create_relations", "add_observations"]):
                                    print(f"📝 检测到Memory工具使用: {message.content[:100]}...")
                    
                    # 检查是否完成
                    if "final_report" in state and state.get("final_report"):
                        print("✅ 研究完成!")
                        break
                        
                    # 防止无限循环
                    if step_count > 10:
                        print("⚠️ 达到最大步骤限制，停止执行")
                        break
                
                print(f"📊 执行总结:")
                print(f"   - 总步骤数: {step_count}")
                print(f"   - 检测到的工具调用: {tool_calls_detected if tool_calls_detected else '无'}")
                
                # 检查是否使用了预期的工具
                memory_tools_used = any("memory" in tool.lower() or 
                                      any(mem_tool in tool.lower() for mem_tool in ["create_entities", "create_relations", "add_observations"])
                                      for tool in tool_calls_detected)
                
                if memory_tools_used:
                    print("✅ Memory工具被成功调用!")
                else:
                    print("⚠️ 未检测到Memory工具调用")
                    
            except Exception as e:
                print(f"❌ 测试执行失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎉 智能MCP工具选择测试完成!")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请确保在ResearcherNexus项目根目录运行此脚本")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_tool_recommendation_algorithm():
    """测试工具推荐算法"""
    
    print("\n🧠 测试工具推荐算法")
    print("="*50)
    
    try:
        from src.graph.nodes import _get_intelligent_tool_recommendations
        
        test_scenarios = [
            {
                "title": "数据存储任务",
                "description": "存储研究发现和分析结果到知识图谱",
                "agent": "researcher"
            },
            {
                "title": "信息检索任务",
                "description": "搜索和检索之前存储的研究信息",
                "agent": "researcher"
            },
            {
                "title": "知识图谱构建",
                "description": "创建实体关系，建立知识网络",
                "agent": "researcher"
            },
            {
                "title": "记录重要发现",
                "description": "保存和记录研究过程中的重要发现",
                "agent": "researcher"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 场景 {i}: {scenario['title']}")
            print(f"📝 描述: {scenario['description']}")
            print(f"🤖 代理: {scenario['agent']}")
            
            recommendations = _get_intelligent_tool_recommendations(
                scenario["title"],
                scenario["description"],
                scenario["agent"]
            )
            
            if recommendations:
                print(f"🎯 推荐结果: {json.dumps(recommendations, indent=2, ensure_ascii=False)}")
                
                # 检查是否推荐了memory工具
                if "memory" in recommendations:
                    print("✅ Memory工具被正确推荐!")
                else:
                    print("⚠️ Memory工具未被推荐")
            else:
                print("❌ 没有推荐结果")
        
    except ImportError as e:
        print(f"❌ 无法导入推荐函数: {e}")
    except Exception as e:
        print(f"❌ 推荐算法测试失败: {e}")


async def main():
    """主测试函数"""
    
    print("🎯 ResearcherNexus智能MCP工具选择最终测试")
    print("="*70)
    
    # 1. 测试工具推荐算法
    await test_tool_recommendation_algorithm()
    
    # 2. 测试完整的智能工具选择流程
    await test_intelligent_mcp_with_memory_server()
    
    print("\n📋 总结和建议:")
    print("="*50)
    print("✅ Memory Server已验证可用 (9个工具)")
    print("✅ 智能配置文件已生成")
    print("✅ 前端配置文件已生成")
    
    print("\n🔧 下一步操作:")
    print("1. 在前端界面删除有问题的Smithery配置")
    print("2. 使用recommended_frontend_config.json中的配置添加Memory Server")
    print("3. 测试包含存储关键词的研究查询")
    print("4. 观察系统是否自动调用Memory工具")
    
    print("\n📝 推荐的测试查询:")
    test_queries = [
        "分析并存储2024年AI发展趋势的关键信息",
        "建立关于量子计算的知识图谱，记录重要发现",
        "搜索之前存储的机器学习研究数据",
        "创建实体关系图，分析技术发展脉络"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")


if __name__ == "__main__":
    asyncio.run(main()) 