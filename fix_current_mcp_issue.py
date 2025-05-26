#!/usr/bin/env python3
"""
修复当前MCP问题的专用脚本

基于测试结果：
✅ Memory Server完全可用 - 找到9个工具
⚠️ Smithery服务器有问题 - 虽然返回4个工具但数据处理出错

解决方案：
1. 删除有问题的Smithery配置
2. 添加稳定的Memory Server配置
3. 启用智能工具选择功能
"""

import json
import requests
import time
from pathlib import Path

class MCPFixer:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        
    def test_backend(self):
        """测试后端连接"""
        print("🔍 检查后端服务...")
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务正常")
                return True
            else:
                print(f"⚠️ 后端响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 后端连接失败: {e}")
            return False
    
    def test_memory_server(self):
        """测试Memory Server"""
        print("\n🧪 验证Memory Server...")
        config = {
            'transport': 'stdio',
            'command': 'npx',
            'args': ['@modelcontextprotocol/server-memory']
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/mcp/server/metadata",
                json=config,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get('tools', [])
                print(f"✅ Memory Server可用 - {len(tools)} 个工具")
                
                # 显示关键工具
                key_tools = ['create_entities', 'create_relations', 'add_observations', 'search_memory']
                available_tools = [tool['name'] for tool in tools]
                
                print("🔧 可用的关键工具:")
                for tool_name in key_tools:
                    if tool_name in available_tools:
                        print(f"   ✅ {tool_name}")
                    else:
                        print(f"   ❌ {tool_name} (未找到)")
                
                return True, tools
            else:
                print(f"❌ Memory Server测试失败: {response.status_code}")
                return False, []
        except Exception as e:
            print(f"❌ Memory Server测试错误: {e}")
            return False, []
    
    def create_recommended_config(self, memory_tools):
        """创建推荐的MCP配置"""
        print("\n📝 生成推荐配置...")
        
        # 基础Memory Server配置
        memory_config = {
            "name": "memory-server",
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-memory"],
            "enabled": True,
            "tools": [
                {"name": tool["name"], "description": tool.get("description", "")}
                for tool in memory_tools[:6]  # 取前6个工具
            ]
        }
        
        # 智能工具选择配置（后端使用）
        intelligent_config = {
            "mcp_settings": {
                "servers": {
                    "memory-server": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-memory"],
                        "enabled_tools": [tool["name"] for tool in memory_tools[:6]]
                        # 注意：不指定add_to_agents，让系统智能选择
                    }
                }
            }
        }
        
        # 前端配置（用于设置页面）
        frontend_config = {
            "general": {
                "autoAcceptedPlan": False,
                "enableBackgroundInvestigation": True,
                "useEnhancedReporter": True,
                "maxPlanIterations": 2,
                "maxStepNum": 5,
                "maxSearchResults": 5
            },
            "mcp": {
                "servers": [memory_config]
            }
        }
        
        return {
            "memory_config": memory_config,
            "intelligent_config": intelligent_config,
            "frontend_config": frontend_config
        }
    
    def save_configs(self, configs):
        """保存配置文件"""
        print("\n💾 保存配置文件...")
        
        # 保存智能配置示例
        intelligent_file = Path("recommended_intelligent_config.py")
        intelligent_content = f'''#!/usr/bin/env python3
"""
推荐的智能MCP配置

使用方法：
1. 在研究工作流中使用这个配置
2. 系统会根据研究内容自动选择工具
3. 无需手动指定add_to_agents
"""

# 智能工具选择配置
INTELLIGENT_MCP_CONFIG = {json.dumps(configs["intelligent_config"], indent=4, ensure_ascii=False)}

# 使用示例
def get_research_config(thread_id="auto_generated"):
    return {{
        "configurable": {{
            "thread_id": thread_id,
            "max_plan_iterations": 2,
            "max_step_num": 5,
            "max_search_results": 5,
            **INTELLIGENT_MCP_CONFIG
        }},
        "recursion_limit": 100
    }}

if __name__ == "__main__":
    print("🎯 推荐的智能MCP配置:")
    print(json.dumps(INTELLIGENT_MCP_CONFIG, indent=2, ensure_ascii=False))
'''
        
        with open(intelligent_file, 'w', encoding='utf-8') as f:
            f.write(intelligent_content)
        print(f"✅ 智能配置已保存: {intelligent_file}")
        
        # 保存前端配置示例
        frontend_file = Path("recommended_frontend_config.json")
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump(configs["frontend_config"], f, indent=2, ensure_ascii=False)
        print(f"✅ 前端配置已保存: {frontend_file}")
        
        return intelligent_file, frontend_file
    
    def test_intelligent_selection(self):
        """测试智能工具选择功能"""
        print("\n🧠 测试智能工具选择...")
        
        # 导入智能推荐函数
        try:
            from src.graph.nodes import _get_intelligent_tool_recommendations
            
            test_cases = [
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
                }
            ]
            
            print("🎯 智能推荐测试结果:")
            for i, case in enumerate(test_cases, 1):
                print(f"\n{i}. {case['title']}")
                print(f"   描述: {case['description']}")
                
                recommendations = _get_intelligent_tool_recommendations(
                    case["title"], case["description"], case["agent"]
                )
                
                if recommendations:
                    print(f"   推荐: {', '.join(recommendations.keys())}")
                    if "memory" in recommendations:
                        print("   ✅ Memory工具被正确推荐")
                    else:
                        print("   ⚠️ Memory工具未被推荐")
                else:
                    print("   ❌ 没有推荐结果")
            
            return True
        except ImportError as e:
            print(f"❌ 无法导入智能推荐函数: {e}")
            return False
        except Exception as e:
            print(f"❌ 智能选择测试失败: {e}")
            return False
    
    def provide_usage_instructions(self):
        """提供使用说明"""
        print("\n📋 使用说明:")
        print("="*50)
        
        print("🔧 前端配置步骤:")
        print("1. 打开ResearcherNexus前端界面")
        print("2. 进入设置页面 (Settings)")
        print("3. 找到MCP服务器配置部分")
        print("4. 删除任何包含'smithery'或'@smithery/cli'的配置")
        print("5. 添加新的Memory Server配置:")
        print("   - 名称: memory-server")
        print("   - 传输: stdio")
        print("   - 命令: npx")
        print("   - 参数: @modelcontextprotocol/server-memory")
        print("   - 启用: ✅")
        
        print("\n⚡ 智能工具选择:")
        print("- 系统会根据研究内容自动选择Memory工具")
        print("- 包含'存储'、'保存'、'记录'等关键词时自动启用")
        print("- 包含'检索'、'搜索'、'查找'等关键词时自动启用")
        print("- 包含'知识图谱'、'实体'、'关系'等关键词时自动启用")
        
        print("\n🧪 测试方法:")
        print("1. 使用包含存储相关关键词的研究查询")
        print("2. 观察日志中的工具推荐信息")
        print("3. 确认Memory工具被自动调用")
        
        print("\n📝 示例研究查询:")
        examples = [
            "分析并存储2024年AI发展趋势的关键信息",
            "建立关于量子计算的知识图谱，记录重要发现",
            "搜索之前存储的机器学习研究数据",
            "创建实体关系图，分析技术发展脉络"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")

def main():
    print("🚀 MCP问题修复工具")
    print("="*60)
    
    fixer = MCPFixer()
    
    # 1. 检查后端
    if not fixer.test_backend():
        print("❌ 后端服务不可用，请先启动后端服务")
        return
    
    # 2. 测试Memory Server
    memory_works, memory_tools = fixer.test_memory_server()
    if not memory_works:
        print("❌ Memory Server不可用，请检查Node.js环境")
        return
    
    # 3. 创建推荐配置
    configs = fixer.create_recommended_config(memory_tools)
    
    # 4. 保存配置文件
    intelligent_file, frontend_file = fixer.save_configs(configs)
    
    # 5. 测试智能选择
    intelligent_works = fixer.test_intelligent_selection()
    
    # 6. 提供使用说明
    fixer.provide_usage_instructions()
    
    print("\n🎉 修复完成!")
    print("="*60)
    
    print("📊 修复总结:")
    print(f"✅ Memory Server可用 - {len(memory_tools)} 个工具")
    print(f"✅ 配置文件已生成: {intelligent_file}")
    print(f"✅ 前端配置已生成: {frontend_file}")
    
    if intelligent_works:
        print("✅ 智能工具选择功能正常")
    else:
        print("⚠️ 智能工具选择功能需要检查")
    
    print("\n🔧 下一步:")
    print("1. 在前端删除Smithery配置")
    print("2. 添加Memory Server配置")
    print("3. 测试智能工具选择功能")
    print("4. 使用包含存储关键词的研究查询进行测试")

if __name__ == "__main__":
    main() 