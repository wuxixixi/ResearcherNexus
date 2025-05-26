#!/usr/bin/env python3
"""
智能MCP工具选择配置示例

这个文件展示了如何配置ResearcherNexus以使用智能MCP工具选择功能，
让系统根据研究内容自动推荐和启用相关的MCP工具。
"""

import asyncio
import logging
from src.graph.builder import build_graph_with_memory

# 设置日志以查看智能选择过程
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 示例1: 基础智能配置
# 系统会根据研究内容自动选择合适的工具
BASIC_INTELLIGENT_CONFIG = {
    "configurable": {
        "thread_id": "intelligent_research_basic",
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "max_search_results": 3,
        "mcp_settings": {
            "servers": {
                # 内存管理工具 - 自动用于需要存储和跟踪的研究
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                    # 注意：不需要指定add_to_agents，系统会智能判断
                },
                
                # 文件系统工具 - 自动用于需要处理文档的研究
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "D:\\ResearcherNexus"],
                    "enabled_tools": ["read_file", "write_file", "list_directory"]
                },
                
                # 搜索工具 - 自动用于需要深度搜索的研究
                "brave-search": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-brave-search"],
                    "enabled_tools": ["web_search"],
                    "env": {
                        "BRAVE_API_KEY": "your-brave-api-key-here"
                    }
                }
            }
        }
    }
}

# 示例2: 混合配置模式
# 结合显式配置和智能选择
HYBRID_CONFIG = {
    "configurable": {
        "thread_id": "intelligent_research_hybrid",
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "max_search_results": 3,
        "mcp_settings": {
            "servers": {
                # 显式配置：始终为特定代理启用
                "citation-manager": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-citation"],
                    "enabled_tools": ["create_citation", "format_bibliography"],
                    "add_to_agents": ["researcher"]  # 显式指定
                },
                
                # 智能配置：根据研究内容自动启用
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                    # 系统会根据研究内容自动判断
                },
                
                "sequential-thinking": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-sequential-thinking"],
                    "enabled_tools": ["think_step_by_step"]
                    # 自动用于需要深度分析的研究
                }
            }
        }
    }
}

# 示例3: 高级智能配置
# 包含多种类型的MCP工具，让系统智能选择
ADVANCED_INTELLIGENT_CONFIG = {
    "configurable": {
        "thread_id": "intelligent_research_advanced",
        "max_plan_iterations": 1,
        "max_step_num": 4,
        "max_search_results": 5,
        "mcp_settings": {
            "servers": {
                # 内存和知识管理
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                },
                
                # 文件系统操作
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "D:\\"],
                    "enabled_tools": ["read_file", "write_file", "list_directory", "search_files"]
                },
                
                # 高级搜索
                "brave-search": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-brave-search"],
                    "enabled_tools": ["web_search"],
                    "env": {
                        "BRAVE_API_KEY": "your-api-key"
                    }
                },
                
                # 数据分析和思考
                "sequential-thinking": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-sequential-thinking"],
                    "enabled_tools": ["think_step_by_step"]
                },
                
                # 时间和日程管理
                "time-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-time"],
                    "enabled_tools": ["get_current_time", "schedule_reminder"]
                },
                
                # 数据库操作（如果需要）
                "sqlite": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-sqlite", "research.db"],
                    "enabled_tools": ["query", "execute", "list_tables"]
                }
            }
        }
    }
}

# 研究场景示例
RESEARCH_SCENARIOS = [
    {
        "name": "AI技术趋势分析",
        "query": "分析2024年人工智能技术的最新发展趋势，包括大语言模型、计算机视觉和机器人技术的进展",
        "expected_tools": ["搜索工具", "内存工具", "分析工具"],
        "config": BASIC_INTELLIGENT_CONFIG
    },
    {
        "name": "本地文档研究",
        "query": "读取本地技术文档，分析其中的API设计模式，并生成最佳实践报告",
        "expected_tools": ["文件系统工具", "内存工具", "分析工具"],
        "config": BASIC_INTELLIGENT_CONFIG
    },
    {
        "name": "学术论文综述",
        "query": "搜索和分析量子计算领域的最新学术论文，整理参考文献并生成综述报告",
        "expected_tools": ["搜索工具", "引用管理工具", "内存工具"],
        "config": HYBRID_CONFIG
    },
    {
        "name": "数据驱动研究",
        "query": "收集市场数据，存储到数据库中，进行统计分析并生成可视化报告",
        "expected_tools": ["搜索工具", "数据库工具", "分析工具", "内存工具"],
        "config": ADVANCED_INTELLIGENT_CONFIG
    }
]

async def run_intelligent_research(scenario):
    """运行智能研究场景"""
    
    print(f"\n🚀 开始研究: {scenario['name']}")
    print(f"📋 查询: {scenario['query']}")
    print(f"🎯 预期工具: {', '.join(scenario['expected_tools'])}")
    print("-" * 60)
    
    # 构建工作流
    graph = build_graph_with_memory()
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": scenario["query"]}],
        "auto_accepted_plan": True,
        "enable_background_investigation": True,
        "locale": "zh-CN"
    }
    
    try:
        # 运行研究工作流
        async for state in graph.astream(initial_state, config=scenario["config"]):
            if "final_report" in state:
                print("✅ 研究完成!")
                print(f"📄 报告长度: {len(state['final_report'])} 字符")
                break
                
    except Exception as e:
        print(f"❌ 研究失败: {e}")
        import traceback
        traceback.print_exc()

async def demonstrate_intelligent_tool_selection():
    """演示智能工具选择功能"""
    
    print("🧠 智能MCP工具选择演示")
    print("=" * 60)
    print("这个演示展示了ResearcherNexus如何根据研究内容自动选择合适的MCP工具")
    print()
    
    # 运行不同的研究场景
    for i, scenario in enumerate(RESEARCH_SCENARIOS):
        print(f"\n📊 场景 {i+1}/{len(RESEARCH_SCENARIOS)}")
        await run_intelligent_research(scenario)
        
        if i < len(RESEARCH_SCENARIOS) - 1:
            print("\n⏳ 等待3秒后继续下一个场景...")
            await asyncio.sleep(3)
    
    print("\n🎉 所有演示完成!")
    print("=" * 60)
    print("📝 智能工具选择的优势:")
    print("1. 🎯 自动匹配：根据研究内容自动选择相关工具")
    print("2. 🔧 减少配置：无需手动指定每个工具的使用场景")
    print("3. 🚀 提高效率：代理主动使用最合适的工具")
    print("4. 📈 优化性能：避免加载不必要的工具")
    print("5. 🧠 智能推荐：基于关键词和上下文的智能推荐")

def show_configuration_examples():
    """显示配置示例"""
    
    print("⚙️ 智能MCP工具配置示例")
    print("=" * 60)
    
    print("\n1. 基础智能配置:")
    print("   - 让系统自动选择大部分工具")
    print("   - 适合一般研究任务")
    print("   - 配置简单，维护成本低")
    
    print("\n2. 混合配置模式:")
    print("   - 结合显式配置和智能选择")
    print("   - 对关键工具进行显式控制")
    print("   - 其他工具由系统智能选择")
    
    print("\n3. 高级智能配置:")
    print("   - 提供丰富的工具选择")
    print("   - 系统根据需要智能启用")
    print("   - 适合复杂的研究项目")
    
    print("\n🔍 智能选择的工作原理:")
    print("1. 分析研究步骤的标题和描述")
    print("2. 识别关键词和研究类型")
    print("3. 匹配相关的工具类别")
    print("4. 根据代理类型过滤工具")
    print("5. 为推荐工具添加上下文指导")

if __name__ == "__main__":
    print("🎯 ResearcherNexus 智能MCP工具选择")
    print("=" * 60)
    
    # 显示配置示例
    show_configuration_examples()
    
    # 运行演示
    asyncio.run(demonstrate_intelligent_tool_selection()) 