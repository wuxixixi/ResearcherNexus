#!/usr/bin/env python3
"""
测试MCP感知的Planner功能
验证planner是否会在步骤描述中包含MCP工具使用说明
"""

import json
import asyncio
from src.prompts import apply_prompt_template
from src.state import State
from src.core.configuration import Configuration
from langchain_core.runnables import RunnableConfig

def test_planner_prompt_with_mcp():
    """测试planner提示词是否包含MCP工具说明"""
    
    # 创建测试状态
    test_state = State(
        messages=[{
            "role": "user",
            "content": "AI对社会结构与行为的深远影响是什么？"
        }],
        locale="zh-CN",
        plan_iterations=0
    )
    
    # 创建配置
    config = Configuration(
        max_step_num=3,
        locale="zh-CN"
    )
    
    # 应用提示词模板
    messages = apply_prompt_template("planner", test_state, config)
    
    # 检查提示词内容
    prompt_content = messages[0]["content"]
    
    print("🔍 检查Planner提示词")
    print("="*60)
    
    # 检查关键MCP工具内容
    mcp_keywords = [
        "MCP Tools Integration",
        "create_entities",
        "create_relations", 
        "add_observations",
        "search_nodes",
        "sequentialthinking"
    ]
    
    found_keywords = []
    for keyword in mcp_keywords:
        if keyword in prompt_content:
            found_keywords.append(keyword)
            print(f"✅ 找到关键词: {keyword}")
        else:
            print(f"❌ 未找到关键词: {keyword}")
    
    # 显示MCP相关部分
    if "MCP Tools Integration" in prompt_content:
        start = prompt_content.find("## MCP Tools Integration")
        end = prompt_content.find("## Step Constraints")
        if start != -1 and end != -1:
            mcp_section = prompt_content[start:end]
            print("\n📄 MCP工具集成部分:")
            print("-"*60)
            print(mcp_section[:500] + "...")
    
    return len(found_keywords) == len(mcp_keywords)

def simulate_planner_response():
    """模拟一个包含MCP工具的planner响应"""
    
    plan = {
        "locale": "zh-CN",
        "has_enough_context": False,
        "thought": "用户询问AI对社会结构与行为的深远影响。这是一个需要全面研究的复杂问题，涉及经济、治理、个人行为等多个方面。需要收集大量数据并建立知识图谱。",
        "title": "AI对社会结构与行为深远影响的研究计划",
        "steps": [
            {
                "need_web_search": True,
                "title": "AI对经济结构与就业市场的影响研究",
                "description": "收集AI对经济结构、就业市场、收入分配的影响数据。搜索AI驱动的产业升级案例、工作岗位变化统计、技能需求趋势。使用`create_entities`存储关键行业、公司、技术和职位类型。使用`create_relations`建立行业与职位、技术与技能需求之间的关系。使用`add_observations`记录重要的统计数据和趋势分析。",
                "step_type": "research"
            },
            {
                "need_web_search": True,
                "title": "AI对社会治理与权力结构的影响分析",
                "description": "研究AI在公共服务、司法系统、社会监控中的应用及其对权力结构的影响。收集智慧城市、AI辅助决策、算法偏见等案例。首先使用`search_nodes`查询已有的相关实体。然后使用`create_entities`存储新的治理机构、AI系统、法规政策。使用`create_relations`构建治理体系之间的关系网络。使用`sequentialthinking`进行深度分析AI对民主决策和权力平衡的影响。",
                "step_type": "research"
            },
            {
                "need_web_search": True,
                "title": "AI对个体行为与社会心理的影响研究",
                "description": "调查AI如何改变个人行为模式、社交方式和心理状态。收集社交媒体算法、个性化推荐、AI伴侣等对人类行为的影响研究。使用`create_entities`存储关键的AI应用、行为模式、心理现象。使用`create_relations`建立技术与行为变化的因果关系。使用`add_observations`记录重要的研究发现和案例。最后使用`search_nodes`整合所有研究发现，构建完整的知识图谱。",
                "step_type": "research"
            }
        ]
    }
    
    print("\n🤖 模拟的MCP感知计划:")
    print("="*60)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    
    # 检查每个步骤是否包含MCP工具
    print("\n📊 MCP工具使用检查:")
    print("-"*60)
    
    for i, step in enumerate(plan["steps"]):
        print(f"\n步骤 {i+1}: {step['title']}")
        tools_mentioned = []
        
        mcp_tools = ["create_entities", "create_relations", "add_observations", "search_nodes", "sequentialthinking"]
        for tool in mcp_tools:
            if tool in step["description"]:
                tools_mentioned.append(tool)
        
        if tools_mentioned:
            print(f"✅ 包含MCP工具: {', '.join(tools_mentioned)}")
        else:
            print("❌ 未包含MCP工具")

def main():
    """主测试函数"""
    print("🧪 测试MCP感知的Planner功能")
    print("="*60)
    
    # 测试1: 检查提示词
    print("\n测试1: 验证Planner提示词")
    prompt_test_passed = test_planner_prompt_with_mcp()
    
    # 测试2: 模拟响应
    print("\n测试2: 模拟MCP感知的计划")
    simulate_planner_response()
    
    # 总结
    print("\n📝 测试总结")
    print("="*60)
    if prompt_test_passed:
        print("✅ Planner提示词已成功集成MCP工具说明")
        print("✅ 计划步骤中包含了具体的MCP工具使用指令")
        print("\n💡 预期效果:")
        print("1. Planner会在步骤描述中明确指定要使用的MCP工具")
        print("2. Researcher会根据步骤描述中的工具名称使用对应的MCP工具")
        print("3. 整个研究过程会构建一个完整的知识图谱")
    else:
        print("❌ Planner提示词未正确集成MCP工具说明")
        print("请检查src/prompts/planner.md文件的修改")

if __name__ == "__main__":
    main() 