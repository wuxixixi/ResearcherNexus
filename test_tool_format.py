import asyncio
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.server.mcp_utils import load_mcp_tools

async def test_tool_format():
    """测试Tool对象的格式"""
    print("测试Tool对象格式...")
    
    try:
        tools = await load_mcp_tools(
            server_type="stdio",
            command="npx",
            args=["@modelcontextprotocol/server-memory"],
            env=None,
            timeout_seconds=60
        )
        
        print(f"获取到 {len(tools)} 个工具:")
        
        if tools:
            first_tool = tools[0]
            print(f"第一个工具的类型: {type(first_tool)}")
            print(f"第一个工具的属性: {dir(first_tool)}")
            print(f"第一个工具的内容: {first_tool}")
            
            # 尝试访问属性
            if hasattr(first_tool, 'name'):
                print(f"工具名称: {first_tool.name}")
            if hasattr(first_tool, 'description'):
                print(f"工具描述: {first_tool.description}")
            if hasattr(first_tool, 'inputSchema'):
                print(f"输入模式: {first_tool.inputSchema}")
                
            # 尝试转换为字典
            if hasattr(first_tool, 'model_dump'):
                tool_dict = first_tool.model_dump()
                print(f"转换为字典: {tool_dict}")
            elif hasattr(first_tool, 'dict'):
                tool_dict = first_tool.dict()
                print(f"转换为字典: {tool_dict}")
            
        return tools
        
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    asyncio.run(test_tool_format()) 