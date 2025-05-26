import requests
import json

def test_memory_server():
    url = "http://localhost:8000/api/mcp/server/metadata"
    data = {
        "transport": "stdio",
        "command": "npx",
        "args": ["@modelcontextprotocol/server-memory"]
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Tools count: {len(result.get('tools', []))}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if len(result.get('tools', [])) > 0:
            print("✅ 成功获取到工具列表!")
            for tool in result['tools']:
                print(f"  - {tool['name']}: {tool['description'][:50]}...")
        else:
            print("❌ 返回空列表")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_memory_server() 