# 智能MCP工具选择使用指南

## 概述

ResearcherNexus现在支持智能MCP工具选择功能，系统能够根据研究内容自动推荐和启用相关的MCP工具，让代理在研究过程中主动调用最合适的工具。

## 🆕 新功能特性

### 1. 智能工具推荐
- 系统分析研究步骤的标题和描述
- 基于关键词匹配自动推荐相关工具
- 根据代理类型（researcher/coder）过滤工具

### 2. 主动工具调用
- 代理在研究过程中主动识别工具使用机会
- 自动组合多个工具以获得最佳效果
- 提供上下文相关的工具使用指导

### 3. 上下文增强
- 为推荐工具添加特定于当前研究步骤的使用指导
- 动态调整工具描述以匹配研究需求

## 快速开始

### 基础配置

只需配置MCP服务器，无需指定`add_to_agents`，系统会智能判断：

```python
config = {
    "configurable": {
        "thread_id": "intelligent_research",
        "mcp_settings": {
            "servers": {
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                    # 系统会根据研究内容自动启用
                },
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "D:\\"],
                    "enabled_tools": ["read_file", "write_file", "list_directory"]
                }
            }
        }
    }
}
```

### 运行研究

```python
import asyncio
from src.graph.builder import build_graph_with_memory

async def run_intelligent_research():
    graph = build_graph_with_memory()
    
    initial_state = {
        "messages": [{"role": "user", "content": "分析本地文档中的数据趋势"}],
        "auto_accepted_plan": True,
        "locale": "zh-CN"
    }
    
    async for state in graph.astream(initial_state, config=config):
        if "final_report" in state:
            print("研究完成!")
            break

asyncio.run(run_intelligent_research())
```

## 工具推荐机制

### 支持的工具类别

| 工具类别 | 触发关键词 | 适用代理 | 优先级 |
|----------|------------|----------|--------|
| 内存管理 | store, remember, track, save, history | researcher, coder | 高 |
| 搜索检索 | search, find, discover, explore, research | researcher | 高 |
| 数据分析 | analyze, process, calculate, statistics | researcher, coder | 中 |
| 文件操作 | file, document, read, write, csv, json | coder, researcher | 中 |
| 数据库 | database, sql, query, table, records | coder | 中 |
| 引用管理 | citation, reference, bibliography, source | researcher | 中 |

### 智能推荐示例

当研究步骤包含以下内容时：

- **"分析销售数据"** → 自动推荐：数据分析工具、内存工具
- **"读取本地文件"** → 自动推荐：文件系统工具、内存工具  
- **"搜索学术论文"** → 自动推荐：搜索工具、引用管理工具
- **"存储研究发现"** → 自动推荐：内存工具、数据库工具

## 配置模式

### 1. 纯智能模式（推荐）

让系统完全自动选择工具：

```python
"mcp_settings": {
    "servers": {
        "memory-server": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-memory"],
            "enabled_tools": ["create_memory", "search_memory"]
            # 无需指定add_to_agents
        }
    }
}
```

### 2. 混合模式

结合显式配置和智能选择：

```python
"mcp_settings": {
    "servers": {
        "citation-manager": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-citation"],
            "enabled_tools": ["create_citation"],
            "add_to_agents": ["researcher"]  # 显式指定
        },
        "memory-server": {
            "transport": "stdio",
            "command": "npx", 
            "args": ["@modelcontextprotocol/server-memory"],
            "enabled_tools": ["create_memory", "search_memory"]
            # 智能选择
        }
    }
}
```

## 实际应用场景

### 场景1：技术文档分析

**研究查询**：分析本地API文档，提取设计模式

**自动启用的工具**：
- 文件系统工具（读取文档）
- 内存工具（存储发现）
- 分析工具（模式识别）

### 场景2：市场趋势研究

**研究查询**：搜索2024年AI市场数据，分析增长趋势

**自动启用的工具**：
- 搜索工具（获取数据）
- 内存工具（存储信息）
- 分析工具（趋势分析）

### 场景3：学术论文综述

**研究查询**：收集量子计算论文，整理参考文献

**自动启用的工具**：
- 搜索工具（论文检索）
- 引用管理工具（文献整理）
- 内存工具（知识管理）

## 调试和监控

### 查看智能推荐日志

启用详细日志以观察智能选择过程：

```python
import logging
logging.basicConfig(level=logging.INFO)

# 在日志中查找以下信息：
# "Intelligent tool recommendations for researcher: ..."
# "Auto-enabling server 'memory-server' for researcher based on intelligent recommendation"
```

### 验证工具使用

检查代理是否主动使用了推荐的工具：

```python
# 在日志中查找：
# "Enhanced researcher with X MCP tools: [tool_names]"
# "🎯 RECOMMENDED for this step: ..."
```

## 最佳实践

### 1. 配置建议
- 优先使用纯智能模式，减少手动配置
- 只对关键工具使用显式配置
- 定期观察日志，了解系统决策

### 2. 研究步骤优化
- 使用清晰、描述性的研究步骤标题
- 在步骤描述中包含相关关键词
- 避免过于模糊的研究目标

### 3. 工具选择优化
- 配置多种类型的MCP工具供系统选择
- 确保工具配置正确且可用
- 定期更新工具版本

## 故障排除

### 常见问题

1. **工具未被自动选择**
   - 检查研究步骤是否包含相关关键词
   - 确认工具配置正确
   - 查看日志中的推荐信息

2. **推荐不准确**
   - 调整研究步骤的描述
   - 使用显式配置覆盖智能选择
   - 反馈给开发团队优化算法

3. **性能问题**
   - 减少配置的工具数量
   - 使用更具体的工具配置
   - 调整超时设置

### 调试命令

```bash
# 运行测试脚本
python test_intelligent_mcp.py

# 查看配置示例
python intelligent_mcp_config_example.py

# 启用详细日志
export PYTHONPATH=. && python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# 运行你的研究代码
"
```

## 未来发展

- 基于机器学习的工具推荐优化
- 动态工具加载和卸载
- 工具使用效果的自动评估
- 更精细的上下文理解

通过智能MCP工具选择功能，ResearcherNexus能够更主动、更智能地使用合适的工具，显著提升研究效率和质量。 