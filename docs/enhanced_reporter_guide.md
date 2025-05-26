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

### 2. MCP工具配置

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

### 3. 完整示例

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

### 3. 质量控制
- 设置合理的超时时间
- 监控工具调用频率
- 验证工具返回的数据质量
- 保持原始信息和增强信息的平衡

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

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 监控工具调用
config["configurable"]["debug_mcp_tools"] = True

# 设置超时
config["configurable"]["mcp_timeout"] = 60
```

## 未来发展

增强版报告员将继续发展，计划添加：
- 更多专业领域的工具支持
- 智能工具选择和优化
- 报告质量评估机制
- 自动化的事实核查流程

通过使用增强版报告员，您可以获得更准确、更全面、更及时的研究报告，显著提升研究工作的质量和效率。 