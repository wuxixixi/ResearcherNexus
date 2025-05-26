#!/usr/bin/env python3
"""
快速MCP测试脚本
"""

import requests
import json

def test_backend():
    """测试后端连接"""
    print("🔍 测试后端连接...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"✅ 后端状态: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_memory_server():
    """测试Memory Server"""
    print("\n🧪 测试Memory Server...")
    config = {
        'transport': 'stdio',
        'command': 'npx',
        'args': ['@modelcontextprotocol/server-memory']
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/mcp/server/metadata',
            json=config,
            timeout=30
        )
        print(f"📡 Memory Server响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('tools', [])
            print(f"✅ 找到 {len(tools)} 个工具")
            
            for tool in tools[:3]:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            return True
        else:
            print(f"❌ 错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Memory Server测试失败: {e}")
        return False

def test_smithery_server():
    """测试Smithery服务器"""
    print("\n🧪 测试Smithery服务器...")
    config = {
        "transport": "stdio",
        "command": "cmd",
        "args": ["/c", "npx", "-y", "@smithery/cli@latest", "run", "@ameeralns/DeepResearchMCP", "--key", "741ccf4e-a807-4366-a4bf-cc8f3a9f277f"]
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/mcp/server/metadata',
            json=config,
            timeout=60
        )
        print(f"📡 Smithery响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('tools', [])
            print(f"✅ 找到 {len(tools)} 个工具")
            
            if tools:
                for tool in tools[:3]:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                return True
            else:
                print("⚠️ 服务器返回空工具列表")
                print("💡 可能原因:")
                print("   - API密钥无效或过期")
                print("   - 服务器内部错误")
                print("   - 权限问题")
                return False
        else:
            print(f"❌ 错误: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时 (60秒)")
        print("💡 可能原因:")
        print("   - 网络连接问题")
        print("   - Smithery服务器响应慢")
        print("   - 防火墙阻止连接")
        return False
    except Exception as e:
        print(f"❌ Smithery测试失败: {e}")
        return False

def main():
    print("🚀 快速MCP诊断")
    print("="*40)
    
    # 测试后端
    if not test_backend():
        print("\n❌ 后端服务不可用，请先启动后端服务")
        return
    
    # 测试Memory Server
    memory_works = test_memory_server()
    
    # 测试Smithery
    smithery_works = test_smithery_server()
    
    # 总结
    print("\n📊 测试总结:")
    print("="*40)
    
    if memory_works:
        print("✅ Memory Server可用 - 推荐使用")
        print("   配置: npx @modelcontextprotocol/server-memory")
    else:
        print("❌ Memory Server不可用")
    
    if smithery_works:
        print("✅ Smithery服务器可用")
    else:
        print("❌ Smithery服务器不可用 - 建议暂时不使用")
    
    print("\n💡 建议:")
    if memory_works:
        print("1. 在前端删除Smithery配置")
        print("2. 添加Memory Server配置:")
        print("   {")
        print('     "transport": "stdio",')
        print('     "command": "npx",')
        print('     "args": ["@modelcontextprotocol/server-memory"]')
        print("   }")
        print("3. 测试智能工具选择功能")
    else:
        print("1. 检查Node.js和npm是否正确安装")
        print("2. 检查网络连接")
        print("3. 尝试手动运行: npx @modelcontextprotocol/server-memory")

if __name__ == "__main__":
    main() 