# 云端MCP服务器列表

以下是一些可以直接使用的云端MCP服务器，无需本地安装：

## 搜索和数据提取

### 1. Brave Search
```json
{
  "mcpServers": {
    "brave-search": {
      "url": "https://api.search.brave.com/mcp/sse"
    }
  }
}
```

### 2. Tavily AI Search
```json
{
  "mcpServers": {
    "tavily-search": {
      "url": "https://api.tavily.com/mcp/sse"
    }
  }
}
```

## 开发工具

### 3. GitHub API
```json
{
  "mcpServers": {
    "github-api": {
      "url": "https://api.github.com/mcp/sse"
    }
  }
}
```

## 数据库服务

### 4. Supabase
```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://your-project.supabase.co/mcp/sse"
    }
  }
}
```

## 注意事项

1. **API密钥**：大多数云端服务需要API密钥
2. **费用**：某些服务可能收费
3. **限制**：注意API调用限制
4. **隐私**：考虑数据隐私问题

## 如何获取API密钥

1. 访问相应服务的官网
2. 注册账户
3. 在开发者控制台获取API密钥
4. 在MCP配置中添加环境变量 