import requests
import json

def test_mcp_server(name, config):
    url = "http://localhost:8000/api/mcp/server/metadata"
    
    try:
        response = requests.post(url, json=config)
        print(f"\n=== 测试 {name} ===")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        tools = result.get('tools', [])
        print(f"Tools count: {len(tools)}")
        
        if len(tools) > 0:
            print("✅ 成功获取到工具列表!")
            for tool in tools[:3]:  # 只显示前3个工具
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
        else:
            print("❌ 返回空列表")
            
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")

def main():
    # 测试一些常见的MCP服务器
    test_configs = [
        ("Sequential Thinking", {
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-sequential-thinking"]
        }),
        ("Memory Server", {
            "transport": "stdio", 
            "command": "npx",
            "args": ["@modelcontextprotocol/server-memory"]
        }),
        ("Filesystem Server", {
            "transport": "stdio",
            "command": "npx", 
            "args": ["@modelcontextprotocol/server-filesystem", "D:\\"]
        }),
        ("Brave Search", {
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-brave-search"]
        })
    ]
    
    print("测试各种MCP服务器...")
    for name, config in test_configs:
        test_mcp_server(name, config)

if __name__ == "__main__":
    main() 