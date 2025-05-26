# Windows环境下的MCP限制

## 问题描述

在Windows环境下，MCP (Model Context Protocol) stdio服务器无法正常工作，这是由于Windows子进程创建的限制导致的已知问题。

## 错误表现

当尝试添加stdio类型的MCP服务器时，您会看到一个错误工具，描述如下：
```
MCP stdio server is not supported on Windows due to subprocess limitations. 
This is a known issue with the current MCP implementation.
```

## 技术原因

这个问题是由于Python的`asyncio.create_subprocess_exec`在Windows环境下抛出`NotImplementedError`异常导致的。这是MCP客户端库在Windows平台上的已知限制。

## 解决方案

### 方案1：使用SSE类型的MCP服务器

推荐使用基于Server-Sent Events (SSE) 的MCP服务器，这些服务器不依赖于子进程创建：

```json
{
  "mcpServers": {
    "example-sse-server": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### 方案2：在Linux/macOS环境中运行

如果您需要使用stdio类型的MCP服务器，建议在Linux或macOS环境中运行ResearcherNexus：

```bash
# 在Linux/macOS中
python server.py
```

### 方案3：使用Docker

您可以使用Docker在Windows上运行Linux容器：

```bash
docker-compose up
```

## 相关资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [MCP服务器列表](https://smithery.ai/)
- [ResearcherNexus Docker配置](../docker-compose.yml)

## 状态

这是MCP库的已知限制，我们正在关注上游的修复进展。一旦MCP库解决了Windows兼容性问题，我们会立即更新支持。 