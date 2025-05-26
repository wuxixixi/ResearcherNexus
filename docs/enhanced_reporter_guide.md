# 增强版报告员使用指南

## 概述

增强版报告员是ResearcherNexus的一个新功能，它在传统报告员的基础上增加了MCP工具支持，能够在报告生成过程中进行实时事实核查、信息补充和质量增强。

## 主要优势

### 1. 实时事实核查
- 在报告生成过程中验证关键数据和统计信息
- 检查最新的发展动态和更新
- 确保报告中的信息准确性和时效性

### 2. 信息补充
- 自动识别信息缺口并进行补充搜索
- 获取额外的背景信息和上下文
- 收集多样化的观点和数据源

### 3. 质量增强
- 使用专业工具进行深度分析
- 改善引用和参考文献管理
- 提供更丰富的数据可视化和表格

### 4. 智能工具选择 🆕
- 系统根据研究内容自动推荐和启用相关MCP工具
- 基于研究步骤的关键词智能匹配工具类型
- 动态调整工具优先级和使用策略

### 5. 主动工具调用 🆕
- 代理在研究过程中主动识别工具使用机会
- 自动组合多个工具以获得最佳研究效果
- 提供上下文相关的工具使用指导

## 使用方法

### 1. 基本配置

在调用API时，在配置中添加 `use_enhanced_reporter: true`：

```python
config = {
    "configurable": {
        "thread_id": "your_thread_id",
        "use_enhanced_reporter": True,  # 启用增强版报告员
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "mcp_settings": {
            "servers": {
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"],
                    "add_to_agents": ["reporter"]  # 添加到报告员代理
                }
            }
        }
    }
}
```

### 2. 智能工具配置 🆕

新版本支持智能工具选择，系统会根据研究内容自动启用相关工具：

```python
config = {
    "configurable": {
        "thread_id": "intelligent_research_001",
        "use_enhanced_reporter": True,
        "max_plan_iterations": 1,
        "max_step_num": 3,
        "mcp_settings": {
            "servers": {
                # 内存管理工具 - 自动用于需要存储和跟踪信息的研究
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                    # 注意：不需要显式指定add_to_agents，系统会智能判断
                },
                
                # 搜索工具 - 自动用于需要深度搜索的研究
                "brave-search": {
                    "transport": "stdio",
                    "command": "npx", 
                    "args": ["@modelcontextprotocol/server-brave-search"],
                    "enabled_tools": ["web_search"]
                },
                
                # 文件系统工具 - 自动用于需要处理文档的研究
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "/path/to/research/docs"],
                    "enabled_tools": ["read_file", "write_file", "list_directory"]
                },
                
                # 数据分析工具 - 自动用于需要数据处理的研究
                "sequential-thinking": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-sequential-thinking"],
                    "enabled_tools": ["think_step_by_step"]
                }
            }
        }
    }
}
```

### 3. 混合配置模式

您可以同时使用显式配置和智能选择：

```python
config = {
    "configurable": {
        "mcp_settings": {
            "servers": {
                # 显式配置：始终为报告员启用
                "citation-manager": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-citation"],
                    "enabled_tools": ["create_citation", "format_bibliography"],
                    "add_to_agents": ["reporter"]  # 显式指定
                },
                
                # 智能配置：根据研究内容自动启用
                "memory-server": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-memory"],
                    "enabled_tools": ["create_memory", "search_memory"]
                    # 系统会根据研究内容自动判断是否启用
                }
            }
        }
    }
}
```

### 4. MCP工具配置

为报告员配置专门的MCP工具：

```python
mcp_settings = {
    "servers": {
        "fact-checker": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@modelcontextprotocol/server-brave-search"],
            "enabled_tools": ["web_search"],
            "add_to_agents": ["reporter"]
        },
        "memory-manager": {
            "transport": "stdio", 
            "command": "npx",
            "args": ["@modelcontextprotocol/server-memory"],
            "enabled_tools": ["create_memory", "search_memory"],
            "add_to_agents": ["reporter"]
        },
        "citation-manager": {
            "transport": "sse",
            "url": "http://localhost:8080/citation-sse",
            "enabled_tools": ["format_citation", "validate_source"],
            "add_to_agents": ["reporter"]
        }
    }
}
```

### 5. 完整示例

```python
import asyncio
from src.graph.builder import build_enhanced_graph_with_memory

async def run_enhanced_research():
    # 构建增强版工作流
    graph = build_enhanced_graph_with_memory()
    
    # 配置
    config = {
        "configurable": {
            "thread_id": "enhanced_research_001",
            "use_enhanced_reporter": True,
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "mcp_settings": {
                "servers": {
                    "brave-search": {
                        "transport": "stdio",
                        "command": "npx", 
                        "args": ["@modelcontextprotocol/server-brave-search"],
                        "enabled_tools": ["web_search"],
                        "add_to_agents": ["reporter"]
                    },
                    "memory-server": {
                        "transport": "stdio",
                        "command": "npx",
                        "args": ["@modelcontextprotocol/server-memory"],
                        "enabled_tools": ["create_memory", "search_memory"],
                        "add_to_agents": ["reporter"]
                    }
                }
            }
        },
        "recursion_limit": 100
    }
    
    # 初始状态
    initial_state = {
        "messages": [{"role": "user", "content": "分析2024年人工智能发展趋势"}],
        "auto_accepted_plan": True,
        "enable_background_investigation": True
    }
    
    # 运行工作流
    async for state in graph.astream(initial_state, config=config):
        if "final_report" in state:
            print("增强版报告生成完成:")
            print(state["final_report"])
            break

# 运行示例
asyncio.run(run_enhanced_research())
```

## 报告质量对比

### 传统报告员
- 仅基于研究团队收集的信息
- 无法进行实时验证
- 信息可能存在时效性问题
- 引用管理相对简单

### 增强版报告员
- 基于研究信息 + 实时工具验证
- 可以补充最新信息和数据
- 具备事实核查能力
- 支持专业的引用和格式化工具
- 能够识别和填补信息缺口

## 智能工具选择机制 🆕

### 工具推荐算法

系统使用以下算法智能推荐MCP工具：

1. **关键词匹配**：分析研究步骤的标题和描述，识别关键词
2. **工具分类**：将工具按功能分类（内存、搜索、分析、文件等）
3. **优先级评分**：根据匹配度和工具重要性计算优先级
4. **代理适配**：确保工具与代理类型兼容

### 支持的工具类别

| 类别 | 关键词示例 | 适用代理 | 优先级 |
|------|------------|----------|--------|
| 内存管理 | store, remember, track, save, history | researcher, coder | 高 |
| 搜索检索 | search, find, discover, explore, research | researcher | 高 |
| 数据分析 | analyze, process, calculate, statistics | researcher, coder | 中 |
| 文件操作 | file, document, read, write, csv, json | coder, researcher | 中 |
| 数据库 | database, sql, query, table, records | coder | 中 |
| 引用管理 | citation, reference, bibliography, source | researcher | 中 |
| Web API | api, web, http, rest, service | coder, researcher | 低 |

### 上下文增强

系统会为推荐的工具添加上下文相关的使用指导：

```
🎯 RECOMMENDED for this step: Store key findings about 'AI发展趋势分析' for later reference and cross-step analysis.
```

## 主动工具调用策略 🆕

### 研究员代理策略

1. **工具发现阶段**：在开始研究前，列出所有可用工具
2. **智能工具选择**：根据研究主题选择最相关的工具
3. **主动工具使用**：
   - 使用内存工具存储重要发现
   - 使用专业搜索工具获取深度信息
   - 使用引用工具管理参考文献
   - 使用分析工具处理数据

### 编码员代理策略

1. **工具评估**：评估可用的编程和数据处理工具
2. **数据管道构建**：
   - 使用文件工具读取数据
   - 使用Python进行核心处理
   - 使用数据库工具存储结果
   - 使用内存工具保存重要计算

### 工具组合模式

系统支持以下工具组合模式：

1. **搜索 + 内存 + 引用**：全面的研究工作流
2. **文件 + 分析 + 内存**：数据处理工作流
3. **搜索 + 分析 + 数据库**：深度分析工作流
4. **API + 处理 + 存储**：外部集成工作流

## 最佳实践

### 1. 工具选择
- **搜索工具**: 用于事实核查和信息更新
- **内存工具**: 用于管理复杂的研究数据
- **分析工具**: 用于深度数据处理
- **格式化工具**: 用于专业的报告格式

### 2. 配置建议
- 为报告员配置3-5个核心工具
- 避免工具过多导致性能问题
- 优先选择可靠性高的工具
- 定期更新工具配置
- **新增**：利用智能工具选择减少手动配置

### 3. 质量控制
- 设置合理的超时时间
- 监控工具调用频率
- 验证工具返回的数据质量
- 保持原始信息和增强信息的平衡
- **新增**：观察智能推荐的工具使用效果

### 4. 智能配置优化 🆕
- 让系统自动选择大部分工具，只手动配置特殊需求
- 观察日志中的工具推荐信息，了解系统决策
- 根据研究类型调整关键词匹配策略
- 定期评估智能选择的准确性

## 故障排除

### 常见问题

1. **MCP工具无法加载**
   - 检查工具配置是否正确
   - 确认网络连接和权限
   - 查看错误日志

2. **报告生成时间过长**
   - 减少启用的工具数量
   - 调整超时设置
   - 优化工具选择

3. **信息质量不佳**
   - 检查工具的可靠性
   - 调整工具优先级
   - 验证数据源质量

4. **智能工具选择不准确** 🆕
   - 检查研究步骤的关键词是否清晰
   - 调整工具分类和关键词匹配规则
   - 使用显式配置覆盖智能选择

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 监控工具调用
config["configurable"]["debug_mcp_tools"] = True

# 设置超时
config["configurable"]["mcp_timeout"] = 60

# 查看智能推荐日志
# 在日志中搜索 "Intelligent tool recommendations" 和 "Auto-enabling server"
```

## 未来发展

增强版报告员将继续发展，计划添加：
- 更多专业领域的工具支持
- 智能工具选择和优化
- 报告质量评估机制
- 自动化的事实核查流程
- **机器学习驱动的工具推荐**：基于历史使用数据优化推荐算法
- **动态工具加载**：根据研究进展动态加载新工具
- **工具性能监控**：实时监控工具使用效果并自动优化

通过使用增强版报告员，您可以获得更准确、更全面、更及时的研究报告，显著提升研究工作的质量和效率。新的智能工具选择功能让系统能够更主动地使用合适的工具，减少手动配置的复杂性。 