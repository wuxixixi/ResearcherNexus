#!/usr/bin/env python3
"""
MCP问题修复脚本

专门用于诊断和修复当前遇到的MCP工具添加问题
"""

import asyncio
import json
import logging
import requests
import subprocess
import time
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPDiagnostic:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = {}
    
    def check_backend_status(self):
        """检查后端服务状态"""
        print("🔍 检查后端服务状态...")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务正常运行")
                return True
            else:
                print(f"⚠️ 后端服务响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到后端服务")
            print("💡 请确保后端服务已启动: python server.py")
            return False
        except Exception as e:
            print(f"❌ 检查后端服务时出错: {e}")
            return False
    
    def check_node_npm_status(self):
        """检查Node.js和npm状态"""
        print("\n🔍 检查Node.js和npm状态...")
        
        try:
            # 检查Node.js
            node_result = subprocess.run(["node", "--version"], 
                                       capture_output=True, text=True, timeout=10)
            if node_result.returncode == 0:
                print(f"✅ Node.js版本: {node_result.stdout.strip()}")
            else:
                print("❌ Node.js未安装或不可用")
                return False
            
            # 检查npm
            npm_result = subprocess.run(["npm", "--version"], 
                                      capture_output=True, text=True, timeout=10)
            if npm_result.returncode == 0:
                print(f"✅ npm版本: {npm_result.stdout.strip()}")
            else:
                print("❌ npm未安装或不可用")
                return False
            
            # 检查npx
            npx_result = subprocess.run(["npx", "--version"], 
                                      capture_output=True, text=True, timeout=10)
            if npx_result.returncode == 0:
                print(f"✅ npx版本: {npx_result.stdout.strip()}")
                return True
            else:
                print("❌ npx未安装或不可用")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 检查Node.js/npm时超时")
            return False
        except FileNotFoundError:
            print("❌ Node.js/npm未找到，请确保已正确安装")
            return False
        except Exception as e:
            print(f"❌ 检查Node.js/npm时出错: {e}")
            return False
    
    def test_simple_mcp_servers(self):
        """测试简单的MCP服务器"""
        print("\n🧪 测试简单的MCP服务器...")
        
        # 推荐的稳定MCP服务器
        stable_servers = [
            {
                "name": "Memory Server",
                "config": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"]
                },
                "description": "内存管理工具，用于存储和检索信息"
            },
            {
                "name": "Sequential Thinking",
                "config": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-sequential-thinking"]
                },
                "description": "顺序思考工具，用于结构化分析"
            },
            {
                "name": "Filesystem Server",
                "config": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "D:\\ResearcherNexus"]
                },
                "description": "文件系统工具，用于读写本地文件"
            }
        ]
        
        working_servers = []
        
        for server in stable_servers:
            print(f"\n🔧 测试 {server['name']}...")
            print(f"   描述: {server['description']}")
            
            try:
                response = requests.post(
                    f"{self.backend_url}/api/mcp/server/metadata",
                    json=server["config"],
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    tools = result.get('tools', [])
                    
                    if tools:
                        print(f"✅ 成功! 获取到 {len(tools)} 个工具")
                        working_servers.append(server)
                        
                        # 显示前3个工具
                        for i, tool in enumerate(tools[:3]):
                            print(f"   {i+1}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                    else:
                        print("⚠️ 服务器启动成功但返回空工具列表")
                else:
                    print(f"❌ 请求失败: HTTP {response.status_code}")
                    if response.text:
                        print(f"   错误信息: {response.text[:200]}...")
                        
            except requests.exceptions.Timeout:
                print("❌ 请求超时 (30秒)")
            except requests.exceptions.ConnectionError:
                print("❌ 连接失败")
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        self.test_results['working_servers'] = working_servers
        return working_servers
    
    def diagnose_smithery_issue(self):
        """诊断Smithery服务器问题"""
        print("\n🔍 诊断Smithery服务器问题...")
        
        problematic_config = {
            "transport": "stdio",
            "command": "cmd",
            "args": ["/c", "npx", "-y", "@smithery/cli@latest", "run", "@ameeralns/DeepResearchMCP", "--key", "741ccf4e-a807-4366-a4bf-cc8f3a9f277f"]
        }
        
        print("🧪 分析问题配置:")
        print(f"   命令: {problematic_config['command']}")
        print(f"   参数: {' '.join(problematic_config['args'])}")
        
        # 分析可能的问题
        print("\n💡 可能的问题分析:")
        
        issues = [
            "1. Smithery CLI需要网络连接下载和运行",
            "2. API密钥可能无效或过期",
            "3. Windows cmd环境可能存在兼容性问题",
            "4. DeepResearchMCP服务器可能不稳定",
            "5. 网络防火墙可能阻止连接"
        ]
        
        for issue in issues:
            print(f"   {issue}")
        
        # 尝试测试
        print("\n📡 尝试测试Smithery配置...")
        try:
            response = requests.post(
                f"{self.backend_url}/api/mcp/server/metadata",
                json=problematic_config,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get('tools', [])
                
                if tools:
                    print(f"✅ 意外成功! 获取到 {len(tools)} 个工具")
                    return True
                else:
                    print("⚠️ 连接成功但返回空工具列表")
                    print("💡 这通常意味着:")
                    print("   - API密钥无效")
                    print("   - 服务器内部错误")
                    print("   - 权限问题")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时 (60秒)")
            print("💡 这通常意味着:")
            print("   - 网络连接问题")
            print("   - Smithery服务器响应慢")
            print("   - 防火墙阻止连接")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        return False
    
    def provide_solutions(self):
        """提供解决方案"""
        print("\n💡 推荐解决方案:")
        print("="*50)
        
        working_servers = self.test_results.get('working_servers', [])
        
        if working_servers:
            print("✅ 好消息! 以下MCP服务器可以正常工作:")
            for server in working_servers:
                print(f"\n🔧 {server['name']}")
                print(f"   配置: {json.dumps(server['config'], ensure_ascii=False)}")
                print(f"   描述: {server['description']}")
        else:
            print("⚠️ 没有找到可工作的MCP服务器")
        
        print("\n📋 建议的操作步骤:")
        
        steps = [
            "1. 暂时停止使用Smithery服务器",
            "2. 使用上面测试成功的稳定MCP服务器",
            "3. 在前端界面中删除有问题的Smithery配置",
            "4. 添加推荐的稳定服务器配置",
            "5. 测试智能工具选择功能"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print("\n🔧 前端配置示例:")
        
        if working_servers:
            example_config = {
                "mcpServers": {}
            }
            
            for server in working_servers[:2]:  # 只显示前2个
                server_key = server['name'].lower().replace(' ', '-')
                example_config["mcpServers"][server_key] = server['config']
            
            print(json.dumps(example_config, indent=2, ensure_ascii=False))
        
        print("\n⚡ 智能工具选择配置:")
        print("使用智能工具选择功能，您只需要配置MCP服务器，")
        print("系统会根据研究内容自动选择合适的工具!")
        
        smart_config_example = {
            "mcp_settings": {
                "servers": {
                    "memory-server": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-memory"],
                        "enabled_tools": ["create_memory", "search_memory"]
                        # 注意：不需要指定add_to_agents，系统会智能判断
                    }
                }
            }
        }
        
        print(json.dumps(smart_config_example, indent=2, ensure_ascii=False))
    
    def create_fix_script(self):
        """创建修复脚本"""
        print("\n📝 创建修复脚本...")
        
        working_servers = self.test_results.get('working_servers', [])
        
        if not working_servers:
            print("⚠️ 没有可用的MCP服务器，无法创建修复脚本")
            return
        
        fix_script_content = f'''#!/usr/bin/env python3
"""
自动生成的MCP修复脚本
生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import requests
import json

def test_and_add_working_servers():
    """测试并添加可工作的MCP服务器"""
    
    backend_url = "http://localhost:8000"
    
    # 可工作的服务器配置
    working_servers = {json.dumps(working_servers, indent=8, ensure_ascii=False)}
    
    print("🔧 测试可工作的MCP服务器...")
    
    for server in working_servers:
        print(f"\\n测试 {{server['name']}}...")
        
        try:
            response = requests.post(
                f"{{backend_url}}/api/mcp/server/metadata",
                json=server["config"],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get('tools', [])
                print(f"✅ 成功! 获取到 {{len(tools)}} 个工具")
            else:
                print(f"❌ 失败: HTTP {{response.status_code}}")
                
        except Exception as e:
            print(f"❌ 错误: {{e}}")
    
    print("\\n💡 推荐在前端使用以下配置:")
    
    frontend_config = {{
        "mcpServers": {{}}
    }}
    
    for server in working_servers:
        key = server['name'].lower().replace(' ', '-')
        frontend_config["mcpServers"][key] = server['config']
    
    print(json.dumps(frontend_config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_and_add_working_servers()
'''
        
        # 保存修复脚本
        fix_script_path = Path("mcp_fix_generated.py")
        with open(fix_script_path, 'w', encoding='utf-8') as f:
            f.write(fix_script_content)
        
        print(f"✅ 修复脚本已保存到: {fix_script_path}")
        print("💡 运行修复脚本: python mcp_fix_generated.py")

async def main():
    """主诊断流程"""
    
    print("🚀 MCP问题诊断和修复工具")
    print("="*60)
    
    diagnostic = MCPDiagnostic()
    
    # 1. 检查基础环境
    print("📋 第一步: 检查基础环境")
    if not diagnostic.check_backend_status():
        print("❌ 后端服务不可用，请先启动后端服务")
        return
    
    if not diagnostic.check_node_npm_status():
        print("❌ Node.js/npm环境不可用，请先安装Node.js")
        return
    
    # 2. 测试稳定的MCP服务器
    print("\n📋 第二步: 测试稳定的MCP服务器")
    working_servers = diagnostic.test_simple_mcp_servers()
    
    # 3. 诊断Smithery问题
    print("\n📋 第三步: 诊断Smithery问题")
    smithery_works = diagnostic.diagnose_smithery_issue()
    
    # 4. 提供解决方案
    print("\n📋 第四步: 提供解决方案")
    diagnostic.provide_solutions()
    
    # 5. 创建修复脚本
    print("\n📋 第五步: 创建修复脚本")
    diagnostic.create_fix_script()
    
    print("\n🎉 诊断完成!")
    print("="*60)
    
    # 总结
    print("📊 诊断总结:")
    if working_servers:
        print(f"✅ 找到 {len(working_servers)} 个可工作的MCP服务器")
        print("💡 建议使用这些稳定的服务器替代Smithery")
    else:
        print("❌ 没有找到可工作的MCP服务器")
        print("💡 请检查网络连接和Node.js环境")
    
    if smithery_works:
        print("✅ Smithery服务器可以工作")
    else:
        print("❌ Smithery服务器存在问题，建议暂时不使用")
    
    print("\n🔧 下一步操作:")
    print("1. 在前端删除有问题的Smithery配置")
    print("2. 添加推荐的稳定MCP服务器")
    print("3. 测试智能工具选择功能")
    print("4. 运行生成的修复脚本验证配置")

if __name__ == "__main__":
    asyncio.run(main()) 