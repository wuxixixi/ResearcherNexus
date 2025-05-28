import requests
import json

def test_mcp_api():
    url = "http://localhost:8000/api/mcp/server/metadata"
    data = {
        "transport": "stdio",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-sequential-thinking"]
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Tools count: {len(result.get('tools', []))}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # 检查是否返回空列表（原来的行为）
        if len(result.get('tools', [])) == 0:
            print("✅ 返回空列表 - 这是原来的行为")
        else:
            print("❌ 返回了工具列表 - 这可能意味着MCP服务器实际上是工作的")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mcp_api() 