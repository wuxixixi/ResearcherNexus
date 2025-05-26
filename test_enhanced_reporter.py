#!/usr/bin/env python3
"""
测试增强版报告员功能
"""

import asyncio
import json
import logging
from src.graph.builder import build_graph_with_memory

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_reporter():
    """测试增强版报告员功能"""
    
    # 构建工作流图
    graph = build_graph_with_memory()
    
    # 配置 - 启用增强版报告员
    config = {
        "configurable": {
            "thread_id": "test_enhanced_reporter_001",
            "use_enhanced_reporter": True,  # 启用增强版报告员
            "max_plan_iterations": 1,
            "max_step_num": 2,
            "max_search_results": 3,
            "mcp_settings": {
                "servers": {
                    "memory-server": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-memory"],
                        "enabled_tools": ["create_memory", "search_memory"],
                        "add_to_agents": ["reporter"]
                    }
                }
            }
        },
        "recursion_limit": 100
    }
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "分析2024年人工智能在医疗领域的最新发展"}],
        "auto_accepted_plan": True,
        "enable_background_investigation": False,
        "locale": "zh-CN"
    }
    
    print("🚀 开始测试增强版报告员...")
    print(f"📋 研究主题: {initial_state['messages'][0]['content']}")
    print(f"⚙️ 配置: 增强版报告员已启用")
    print("-" * 50)
    
    try:
        # 运行工作流
        final_state = None
        step_count = 0
        
        async for state in graph.astream(initial_state, config=config):
            step_count += 1
            print(f"📍 步骤 {step_count}: {list(state.keys())}")
            
            # 检查是否有最终报告
            if "final_report" in state:
                final_state = state
                print("✅ 增强版报告生成完成!")
                break
                
            # 检查是否有错误
            if "__end__" in state:
                print("⚠️ 工作流结束，但没有生成报告")
                break
        
        if final_state and "final_report" in final_state:
            report = final_state["final_report"]
            print("\n" + "="*60)
            print("📊 增强版报告内容:")
            print("="*60)
            print(report)
            print("="*60)
            
            # 检查报告是否包含增强功能的特征
            enhanced_features = []
            if "增强发现" in report or "Enhanced Findings" in report:
                enhanced_features.append("✅ 包含增强发现部分")
            if "工具验证" in report or "tool-verified" in report:
                enhanced_features.append("✅ 包含工具验证信息")
            if "事实核查" in report or "fact-check" in report:
                enhanced_features.append("✅ 包含事实核查")
            
            print(f"\n🔍 增强功能检测:")
            if enhanced_features:
                for feature in enhanced_features:
                    print(f"  {feature}")
            else:
                print("  ⚠️ 未检测到明显的增强功能特征")
                
        else:
            print("❌ 测试失败: 没有生成最终报告")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        logger.exception("测试失败")

async def test_normal_reporter():
    """测试普通报告员作为对比"""
    
    # 构建工作流图
    graph = build_graph_with_memory()
    
    # 配置 - 不启用增强版报告员
    config = {
        "configurable": {
            "thread_id": "test_normal_reporter_001",
            "use_enhanced_reporter": False,  # 不启用增强版报告员
            "max_plan_iterations": 1,
            "max_step_num": 2,
            "max_search_results": 3,
        },
        "recursion_limit": 100
    }
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "分析2024年人工智能在医疗领域的最新发展"}],
        "auto_accepted_plan": True,
        "enable_background_investigation": False,
        "locale": "zh-CN"
    }
    
    print("\n🔄 开始测试普通报告员（对比）...")
    print(f"📋 研究主题: {initial_state['messages'][0]['content']}")
    print(f"⚙️ 配置: 普通报告员")
    print("-" * 50)
    
    try:
        # 运行工作流
        final_state = None
        step_count = 0
        
        async for state in graph.astream(initial_state, config=config):
            step_count += 1
            print(f"📍 步骤 {step_count}: {list(state.keys())}")
            
            # 检查是否有最终报告
            if "final_report" in state:
                final_state = state
                print("✅ 普通报告生成完成!")
                break
                
            # 检查是否有错误
            if "__end__" in state:
                print("⚠️ 工作流结束，但没有生成报告")
                break
        
        if final_state and "final_report" in final_state:
            report = final_state["final_report"]
            print(f"\n📄 普通报告长度: {len(report)} 字符")
            print("📝 普通报告预览 (前200字符):")
            print("-" * 40)
            print(report[:200] + "..." if len(report) > 200 else report)
            print("-" * 40)
                
        else:
            print("❌ 对比测试失败: 没有生成最终报告")
            
    except Exception as e:
        print(f"❌ 对比测试过程中出现错误: {e}")
        logger.exception("对比测试失败")

async def main():
    """主函数"""
    print("🧪 增强版报告员功能测试")
    print("=" * 60)
    
    # 测试增强版报告员
    await test_enhanced_reporter()
    
    # 测试普通报告员作为对比
    await test_normal_reporter()
    
    print("\n🏁 测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 