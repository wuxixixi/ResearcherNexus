import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.server.mcp_request import MCPServerMetadataRequest
from src.server.app import mcp_server_metadata

async def test_direct_api():
    """直接测试FastAPI端点"""
    print("直接测试FastAPI端点...")
    
    request = MCPServerMetadataRequest(
        transport="stdio",
        command="npx",
        args=["@modelcontextprotocol/server-memory"],
        url=None,
        env=None,
        timeout_seconds=60
    )
    
    try:
        response = await mcp_server_metadata(request)
        print(f"获取到 {len(response.tools)} 个工具:")
        for tool in response.tools:
            if isinstance(tool, dict):
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            else:
                print(f"  - {tool}")
        return response
        
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_direct_api()) 