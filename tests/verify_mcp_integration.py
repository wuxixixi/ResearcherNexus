#!/usr/bin/env python3
"""
验证MCP工具集成到planner和researcher提示词中
"""

def check_planner_md():
    """检查planner.md文件是否包含MCP工具说明"""
    print("🔍 检查 src/prompts/planner.md")
    print("="*60)
    
    try:
        with open("src/prompts/planner.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键内容
        checks = {
            "MCP Tools Integration": "MCP工具集成部分",
            "create_entities": "create_entities工具",
            "create_relations": "create_relations工具",
            "add_observations": "add_observations工具",
            "search_nodes": "search_nodes工具",
            "sequentialthinking": "sequentialthinking工具",
            "Good Step Description": "好的步骤描述示例",
            "Poor Step Description": "差的步骤描述示例"
        }
        
        all_found = True
        for key, desc in checks.items():
            if key in content:
                print(f"✅ 找到: {desc}")
            else:
                print(f"❌ 未找到: {desc}")
                all_found = False
        
        # 显示MCP部分
        if "MCP Tools Integration" in content:
            start = content.find("## MCP Tools Integration")
            end = content.find("## Step Constraints")
            if start != -1 and end != -1:
                mcp_section = content[start:end]
                print(f"\n📄 MCP工具集成部分预览 (前500字符):")
                print("-"*60)
                print(mcp_section[:500] + "...")
        
        return all_found
        
    except FileNotFoundError:
        print("❌ 文件不存在: src/prompts/planner.md")
        return False

def check_researcher_md():
    """检查researcher.md文件是否包含MCP工具使用说明"""
    print("\n\n🔍 检查 src/prompts/researcher.md")
    print("="*60)
    
    try:
        with open("src/prompts/researcher.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查关键内容
        checks = {
            "MCP Tool Usage Instructions": "MCP工具使用说明",
            "When mentioned, extract and store key entities": "create_entities使用说明",
            "When specified, establish relationships": "create_relations使用说明",
            "When requested, record important findings": "add_observations使用说明",
            "When instructed, query the knowledge graph": "search_nodes使用说明",
            "When indicated, use for deep analysis": "sequentialthinking使用说明",
            "using them is MANDATORY": "强制使用说明"
        }
        
        all_found = True
        for key, desc in checks.items():
            if key in content:
                print(f"✅ 找到: {desc}")
            else:
                print(f"❌ 未找到: {desc}")
                all_found = False
        
        # 显示MCP部分
        if "MCP Tool Usage Instructions" in content:
            start = content.find("## MCP Tool Usage Instructions")
            end = content.find("## How to Use Dynamic Loaded Tools")
            if start != -1 and end != -1:
                mcp_section = content[start:end]
                print(f"\n📄 MCP工具使用说明预览:")
                print("-"*60)
                print(mcp_section)
        
        return all_found
        
    except FileNotFoundError:
        print("❌ 文件不存在: src/prompts/researcher.md")
        return False

def show_expected_plan_example():
    """显示预期的包含MCP工具的计划示例"""
    print("\n\n🤖 预期的MCP感知计划示例")
    print("="*60)
    
    example = """
{
  "locale": "zh-CN",
  "has_enough_context": false,
  "thought": "用户询问AI对社会结构与行为的深远影响...",
  "title": "AI对社会结构与行为深远影响的研究计划",
  "steps": [
    {
      "need_web_search": true,
      "title": "AI对经济结构与就业市场的影响研究",
      "description": "收集AI对经济结构、就业市场、收入分配的影响数据。搜索AI驱动的产业升级案例、工作岗位变化统计、技能需求趋势。使用`create_entities`存储关键行业、公司、技术和职位类型。使用`create_relations`建立行业与职位、技术与技能需求之间的关系。使用`add_observations`记录重要的统计数据和趋势分析。",
      "step_type": "research"
    }
  ]
}
"""
    print(example)
    
    print("\n💡 关键点:")
    print("1. 步骤描述中明确包含了MCP工具名称（用反引号标记）")
    print("2. 说明了每个工具的具体用途")
    print("3. 工具使用遵循逻辑顺序：先创建实体，再建立关系，最后记录观察")

def main():
    """主函数"""
    print("🧪 验证MCP工具集成")
    print("="*60)
    
    # 检查文件修改
    planner_ok = check_planner_md()
    researcher_ok = check_researcher_md()
    
    # 显示示例
    show_expected_plan_example()
    
    # 总结
    print("\n\n📝 验证总结")
    print("="*60)
    
    if planner_ok and researcher_ok:
        print("✅ MCP工具已成功集成到提示词中！")
        print("\n🎯 预期效果:")
        print("1. Planner会在生成计划时，在步骤描述中包含具体的MCP工具")
        print("2. Researcher看到工具名称后会强制使用这些工具")
        print("3. 整个研究过程会构建知识图谱，实现信息的结构化存储")
        print("\n⚡ 下一步:")
        print("1. 重启服务以加载新的提示词")
        print("2. 在Web界面测试AI研究任务")
        print("3. 观察计划中是否包含MCP工具指令")
    else:
        print("❌ MCP工具集成不完整")
        if not planner_ok:
            print("   - 请检查 src/prompts/planner.md 的修改")
        if not researcher_ok:
            print("   - 请检查 src/prompts/researcher.md 的修改")

if __name__ == "__main__":
    main() 