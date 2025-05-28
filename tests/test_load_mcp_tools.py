import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.server.mcp_utils import load_mcp_tools

async def test_load_mcp_tools():
    """直接测试load_mcp_tools函数"""
    print("测试load_mcp_tools函数...")
    
    try:
        tools = await load_mcp_tools(
            server_type="stdio",
            command="npx",
            args=["@modelcontextprotocol/server-memory"],
            env=None,
            timeout_seconds=60
        )
        
        print(f"获取到 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
            
        return tools
        
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(test_load_mcp_tools()) 