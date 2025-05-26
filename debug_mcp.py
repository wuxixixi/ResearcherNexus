import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 设置详细的日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_mcp_direct():
    """直接测试MCP连接，不通过HTTP API"""
    try:
        print("开始测试MCP连接...")
        
        server_params = StdioServerParameters(
            command="npx",
            args=["@modelcontextprotocol/server-memory"],
            env=None,
        )
        
        print(f"服务器参数: {server_params}")
        
        async with stdio_client(server_params) as (read, write):
            print("成功创建stdio客户端")
            
            async with ClientSession(read, write) as session:
                print("成功创建客户端会话")
                
                # 初始化连接
                await session.initialize()
                print("成功初始化连接")
                
                # 列出工具
                tools_result = await session.list_tools()
                print(f"获取到 {len(tools_result.tools)} 个工具:")
                
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                    
                return tools_result.tools
                
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(test_mcp_direct()) 