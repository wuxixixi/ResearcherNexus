# MCP服务器故障排除指南

## 概述

本指南帮助您解决在ResearcherNexus中添加MCP服务器时遇到的问题。

## 常见问题与解决方案

### 1. "服务器没有返回任何工具"错误

**错误信息：**
```
服务器 "your-server-name" 没有返回任何工具。这可能是因为：
1. 服务器启动失败
2. 命令或参数不正确
3. Windows环境下的兼容性问题
4. 网络连接问题

请检查服务器配置或查看控制台日志获取更多信息。
```

**可能原因：**

#### A. 服务器启动失败
- **检查方法：** 在命令行中手动运行MCP服务器命令
- **解决方案：** 确保所有依赖项已正确安装

```bash
# 例如，测试memory server
npx @modelcontextprotocol/server-memory
```

#### B. 命令或参数不正确
- **检查方法：** 验证JSON配置中的command和args字段
- **解决方案：** 参考官方文档确认正确的命令格式

**正确示例：**
```json
{
  "mcpServers": {
    "memory-server": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"]
    }
  }
}
```

**错误示例：**
```json
{
  "mcpServers": {
    "memory-server": {
      "command": "@modelcontextprotocol/server-memory"  // ❌ 缺少npx
    }
  }
}
```

#### C. Windows环境兼容性问题
某些MCP服务器在Windows环境下可能不兼容。

**推荐的Windows兼容服务器：**
- `@modelcontextprotocol/server-memory` ✅
- `@modelcontextprotocol/server-filesystem` ✅
- `@modelcontextprotocol/server-brave-search` ✅

**已知不兼容的服务器：**
- 某些需要Unix特定功能的服务器 ❌

#### D. 网络连接问题
- **检查方法：** 确保能够访问npm registry
- **解决方案：** 检查网络连接和防火墙设置

### 2. 添加界面一直显示加载状态

**原因：** 这通常是因为MCP服务器启动超时或失败，但前端没有收到明确的错误信息。

**解决方案：**
1. 等待加载完成（最多5分钟）
2. 如果仍然加载，刷新页面重试
3. 检查浏览器控制台的错误信息
4. 检查后端日志

### 3. 服务器添加成功但没有工具显示

**原因：** 服务器启动成功但没有暴露任何工具。

**解决方案：**
1. 检查服务器文档确认是否需要额外配置
2. 验证环境变量是否正确设置
3. 检查服务器版本是否兼容

## 推荐的MCP服务器配置

### 基础配置（适用于大多数用户）

```json
{
  "mcpServers": {
    "memory-server": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"]
    },
    "filesystem-server": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\YourUsername\\Documents"
      ]
    }
  }
}
```

### 高级配置（包含环境变量）

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 调试步骤

### 1. 检查后端日志

启动后端时查看控制台输出：
```bash
python server.py
```

查找类似以下的日志信息：
```
INFO:src.server.app:MCP server metadata request: ...
WARNING:src.server.mcp_utils:Failed to load MCP tools: ...
INFO:src.server.app:Loaded X tools from MCP server
```

### 2. 手动测试MCP服务器

在命令行中直接运行MCP服务器：
```bash
npx @modelcontextprotocol/server-memory
```

如果成功，您应该看到服务器启动信息。

### 3. 检查依赖项

确保Node.js和npm已正确安装：
```bash
node --version
npm --version
npx --version
```

### 4. 使用测试脚本

运行项目提供的测试脚本：
```bash
python test_mcp_frontend_fix.py
```

## 获取帮助

如果问题仍然存在：

1. **查看官方文档：** [MCP官方网站](https://modelcontextprotocol.io/)
2. **搜索MCP服务器：** [Smithery.ai](https://smithery.ai/)
3. **提交Issue：** 在ResearcherNexus GitHub仓库中提交问题
4. **包含信息：**
   - 操作系统版本
   - Node.js版本
   - 完整的错误日志
   - 尝试添加的MCP服务器配置

## 更新日志

- **2025-01-26：** 改进了前端错误处理，现在会显示详细的错误信息
- **2025-01-26：** 添加了Windows环境特定的配置示例
- **2025-01-26：** 改进了错误信息的显示格式 