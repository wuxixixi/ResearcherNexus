# MCP工具添加问题解决方案

## 问题诊断结果

根据测试结果，我们发现：

✅ **Memory Server完全可用** - 找到9个工具，包括：
- create_entities: 创建知识图谱实体
- create_relations: 创建实体关系
- add_observations: 添加观察数据

⚠️ **Smithery服务器有问题** - 虽然能连接但数据处理有错误

## 立即解决方案

### 第一步：删除有问题的Smithery配置

1. 打开ResearcherNexus前端界面
2. 进入设置页面
3. 找到MCP服务器配置
4. 删除包含`@smithery/cli`的配置

### 第二步：添加稳定的Memory Server

在前端MCP配置中添加以下配置：

```json
{
  "transport": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-memory"]
}
```

### 第三步：测试智能工具选择

使用以下配置测试智能工具选择功能：

```python
config = {
    "configurable": {
        "thread_id": "test_intelligent_mcp",
        "mcp_settings": {
            "servers": {
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_entities", "create_relations", "add_observations"]
                    # 注意：不需要指定add_to_agents，系统会智能判断
                }
            }
        }
    }
}
```

## 推荐的MCP服务器配置

### 1. Memory Server（强烈推荐）
```json
{
  "name": "Memory Server",
  "transport": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-memory"],
  "description": "知识图谱和内存管理工具"
}
```

### 2. Sequential Thinking
```json
{
  "name": "Sequential Thinking",
  "transport": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-sequential-thinking"],
  "description": "结构化思考和分析工具"
}
```

### 3. Filesystem Server
```json
{
  "name": "Filesystem Server",
  "transport": "stdio",
  "command": "npx",
  "args": ["@modelcontextprotocol/server-filesystem", "D:\\ResearcherNexus"],
  "description": "本地文件系统访问工具"
}
```

## 智能工具选择配置示例

### 基础智能配置
```python
{
    "mcp_settings": {
        "servers": {
            "memory-server": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-memory"],
                "enabled_tools": ["create_entities", "create_relations", "add_observations"]
                # 系统会根据研究内容自动启用
            }
        }
    }
}
```

### 高级智能配置
```python
{
    "mcp_settings": {
        "servers": {
            "memory-server": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-memory"],
                "enabled_tools": ["create_entities", "create_relations", "add_observations"]
            },
            "sequential-thinking": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-sequential-thinking"],
                "enabled_tools": ["think_step_by_step"]
            },
            "filesystem": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "D:\\ResearcherNexus"],
                "enabled_tools": ["read_file", "write_file", "list_directory"]
            }
        }
    }
}
```

## 智能工具选择的工作原理

系统会根据研究步骤的内容自动推荐工具：

### 触发关键词示例

| 研究内容 | 自动启用的工具 | 原因 |
|----------|----------------|------|
| "存储研究发现" | Memory Server | 包含"存储"关键词 |
| "分析数据趋势" | Memory Server + Sequential Thinking | 包含"分析"关键词 |
| "读取本地文件" | Filesystem Server | 包含"文件"关键词 |
| "建立知识图谱" | Memory Server | 包含"知识"关键词 |

### 上下文增强示例

当系统推荐Memory Server时，会添加上下文指导：

```
🎯 RECOMMENDED for this step: Store key findings about 'AI发展趋势分析' for later reference and cross-step analysis.
```

## 测试步骤

### 1. 验证配置
运行以下命令验证配置：
```bash
python quick_mcp_test.py
```

### 2. 测试智能选择
运行以下命令测试智能工具选择：
```bash
python test_intelligent_mcp.py
```

### 3. 完整研究测试
```python
# 使用智能配置进行研究
query = "分析并存储2024年AI技术发展的关键信息"
# 系统会自动选择Memory Server用于存储功能
```

## 故障排除

### 如果Memory Server无法工作

1. 检查Node.js安装：
```bash
node --version
npm --version
npx --version
```

2. 手动测试Memory Server：
```bash
npx @modelcontextprotocol/server-memory
```

3. 检查网络连接和防火墙设置

### 如果智能选择不工作

1. 检查研究步骤是否包含相关关键词
2. 查看日志中的推荐信息：
```
"Intelligent tool recommendations for researcher: ..."
"Auto-enabling server 'memory-server' for researcher based on intelligent recommendation"
```

3. 使用显式配置覆盖智能选择

## 总结

通过以上步骤，您可以：

1. ✅ 解决当前的Smithery服务器问题
2. ✅ 使用稳定的Memory Server
3. ✅ 启用智能工具选择功能
4. ✅ 让系统根据研究内容主动调用合适的MCP工具

智能工具选择功能已经完全实现，只需要配置可用的MCP服务器，系统就会根据研究内容自动推荐和启用相关工具！ 