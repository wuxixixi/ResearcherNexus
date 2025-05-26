# Windows环境下可用的SSE类型MCP服务器示例

由于Windows环境下stdio类型的MCP服务器无法正常工作，以下是一些可以在Windows上使用的SSE（Server-Sent Events）类型MCP服务器示例：

## 如何使用SSE类型服务器

在ResearcherNexus的设置页面中，选择"添加服务"，然后使用以下格式：

```json
{
  "mcpServers": {
    "服务器名称": {
      "url": "http://localhost:端口/sse"
    }
  }
}
```

## 可用的SSE服务器示例

### 1. 本地文件服务器
如果您有一个本地运行的MCP SSE服务器：
```json
{
  "mcpServers": {
    "local-file-server": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### 2. Web API服务器
连接到远程API服务：
```json
{
  "mcpServers": {
    "api-server": {
      "url": "https://api.example.com/mcp/sse"
    }
  }
}
```

### 3. 数据库服务器
连接到数据库服务：
```json
{
  "mcpServers": {
    "database-server": {
      "url": "http://localhost:3000/mcp/sse"
    }
  }
}
```

## 创建自己的SSE MCP服务器

如果您想创建自己的SSE类型MCP服务器，可以参考以下资源：

### Python示例
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI()

@app.get("/sse")
async def sse_endpoint():
    async def event_stream():
        # 实现您的MCP服务器逻辑
        tools = [
            {
                "name": "example_tool",
                "description": "示例工具",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        ]
        
        # 发送工具列表
        yield f"data: {json.dumps({'tools': tools})}\n\n"
        
        # 保持连接
        while True:
            await asyncio.sleep(1)
            yield f"data: {json.dumps({'heartbeat': True})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Node.js示例
```javascript
const express = require('express');
const app = express();

app.get('/sse', (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    });

    // 发送工具列表
    const tools = [
        {
            name: "example_tool",
            description: "示例工具",
            inputSchema: {
                type: "object",
                properties: {
                    input: { type: "string" }
                }
            }
        }
    ];

    res.write(`data: ${JSON.stringify({ tools })}\n\n`);

    // 保持连接
    const heartbeat = setInterval(() => {
        res.write(`data: ${JSON.stringify({ heartbeat: true })}\n\n`);
    }, 30000);

    req.on('close', () => {
        clearInterval(heartbeat);
    });
});

app.listen(8080, () => {
    console.log('SSE MCP Server running on port 8080');
});
```

## 注意事项

1. **端口配置**：确保您的SSE服务器运行在可访问的端口上
2. **CORS设置**：如果从浏览器访问，需要正确配置CORS
3. **认证**：生产环境中应该添加适当的认证机制
4. **错误处理**：实现适当的错误处理和重连机制

## 相关资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [SSE规范](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI SSE文档](https://fastapi.tiangolo.com/advanced/server-sent-events/)
- [Express.js SSE示例](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) 