# 🔍 ResearcherNexus

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](./README_en.md) | [简体中文](./README.md) | [日本語](./README_ja.md)

> 源于开源，回馈开源。

**ResearcherNexus**是一个社区驱动的深度研究框架，将语言模型与专业工具结合，用于网络搜索、网页爬取和Python代码执行等任务，同时回馈使这一切成为可能的开源社区。**ResearcherNexus**使用现代化的[多代理系统](https://zhida.zhihu.com/search?content_id=257568510&content_type=Article&match_order=1&q=多代理系统&zhida_source=entity)架构，通过[LangGraph](https://zhida.zhihu.com/search?content_id=257568510&content_type=Article&match_order=1&q=LangGraph&zhida_source=entity)框架实现灵活的基于状态的工作流程，通过一套明确定义的消息传递系统实现组件间通信。其核心设计思想是将复杂的研究过程拆分为可管理的阶段，由专门的AI代理负责处理，从而实现高效、全面的自动化研究。

请访问[ResearcherNexus的官方网站](https://www.SASS.org.cn/)了解更多详情。

## 新增功能

### 用户认证系统

ResearcherNexus现在支持用户登录和注册功能，提供了简单且安全的认证机制：

- **用户登录**：用户可以通过用户名和密码进行登录
- **用户注册**：新用户可以创建账号，提供用户名、邮箱和密码
- **权限控制**：未登录用户将被引导至登录页面，只有认证用户才能访问核心功能
- **用户信息**：登录后，用户可以在界面中查看其个人信息
- **安全退出**：用户可以安全退出系统

通过主页的"开始使用"按钮，您将被引导至登录页面，完成身份验证后即可使用所有研究工具。

### 用户使用限制功能

为了更好地管理系统资源，ResearcherNexus现在支持用户使用限制：

- **消息使用限制**：普通用户每日可发送的消息数量有上限（默认为10条）
- **实时使用追踪**：用户可以在界面上查看自己的使用情况（已使用/剩余量）
- **使用限制提示**：当用户达到使用限制时，系统会显示友好的提示信息

### 管理员后台系统

ResearcherNexus新增了管理员后台，提供以下功能：

- **用户管理**：管理员可以查看、编辑和删除系统中的所有用户
- **使用限制管理**：管理员可以调整用户的每日使用限制
- **默认管理员账户**：系统自动创建默认管理员（用户名: `admin`，密码: `admin123`）
- **权限控制**：只有管理员才能访问管理后台（`/admin`路径）

管理员可以通过访问 `/admin` 路径进入管理后台，执行上述管理操作。

## 项目价值

ResearcherNexus定位为一个深度研究框架，专注于以下几个方面：

1. **自动化研究流程**：将复杂的研究任务分解为可管理的步骤，并由专门的代理自动执行。
2. **多模态内容创建**：支持生成研究报告、播客和演示文稿等多种类型的内容。
3. **[人机协作](https://zhida.zhihu.com/search?content_id=257568510&content_type=Article&match_order=1&q=人机协作&zhida_source=entity)**：通过人在环系统(human-in-the-loop)，使用户能够以自然语言交互方式修改研究计划。
4. **工具融合**：无缝集成各种研究工具和方法，**支持MCP**，包括网络搜索、网页爬取和代码执行等。

---


## 📑 目录

- [🚀 快速开始](#快速开始)
- [🌟 特性](#特性)
- [🏗️ 架构](#架构)
- [🔄 LangSmith集成](#langsmith集成)
- [🛠️ 开发](#开发)
- [🗣️ 文本转语音集成](#文本转语音集成)
- [📚 示例](#示例)
- [❓ 常见问题](#常见问题)
- [📜 许可证](#许可证)
- [💖 致谢](#致谢)
- [⭐ Star History](#star-History)


## 快速开始

ResearcherNexus使用Python开发，并配有用Node.js编写的Web UI。为确保顺利的设置过程，我们推荐使用以下工具：

### 推荐工具
- **[`uv`](https://docs.astral.sh/uv/getting-started/installation/):**
  简化Python环境和依赖管理。`uv`会自动在根目录创建虚拟环境并为您安装所有必需的包—无需手动安装Python环境。

- **[`nvm`](https://github.com/nvm-sh/nvm):**
  轻松管理多个Node.js运行时版本。

- **[`pnpm`](https://pnpm.io/installation):**
  安装和管理Node.js项目的依赖。

### 环境要求
确保您的系统满足以下最低要求：
- **[Python](https://www.python.org/downloads/):** 版本 `3.12+`
- **[Node.js](https://nodejs.org/en/download/):** 版本 `22+`

### 安装
```bash
# 克隆仓库
git clone 🔍https://github.com/wuxixixi/ResearcherNexus.git
cd ResearcherNexus

# 安装依赖，uv将负责Python解释器和虚拟环境的创建，并安装所需的包
uv sync

# 使用您的API密钥配置.env
# Tavily: https://app.tavily.com/home
# Brave_SEARCH: https://brave.com/search/api/
# 火山引擎TTS: 如果您有TTS凭证，请添加
cp .env.example .env

# 查看下方的"支持的搜索引擎"和"文本转语音集成"部分了解所有可用选项

# 为您的LLM模型和API密钥配置conf.yaml
# 请参阅'docs/configuration_guide.md'获取更多详情
cp conf.yaml.example conf.yaml

# 安装marp用于PPT生成
# https://github.com/marp-team/marp-cli?tab=readme-ov-file#use-package-manager
brew install marp-cli
```

可选，通过[pnpm](https://pnpm.io/installation)安装Web UI依赖：

```bash
cd ResearcherNexus/web
pnpm install
```

### 配置

请参阅[配置指南](docs/configuration_guide.md)获取更多详情。

> [!注意]
> 在启动项目之前，请仔细阅读指南，并更新配置以匹配您的特定设置和要求。

### 控制台UI

运行项目的最快方法是使用控制台UI。

```bash
# 在类bash的shell中运行项目
uv run main.py
```

### Web UI

本项目还包括一个Web UI，提供更加动态和引人入胜的交互体验。
> [!注意]
> 您需要先安装Web UI的依赖。

```bash
# 在开发模式下同时运行后端和前端服务器
# 在macOS/Linux上
./bootstrap.sh -d

# 在Windows上
bootstrap.bat -d
```

打开浏览器并访问[`http://localhost:3000`](http://localhost:3000)探索Web UI。

在[`web`](./web/)目录中探索更多详情。


## 支持的搜索引擎

RearcherNexus支持多种搜索引擎，可以在`.env`文件中通过`SEARCH_API`变量进行配置：

- **Tavily**（默认）：专为AI应用设计的专业搜索API
    - 需要在`.env`文件中设置`TAVILY_API_KEY`
    - 注册地址：https://app.tavily.com/home

- **DuckDuckGo**：注重隐私的搜索引擎
    - 无需API密钥

- **Brave Search**：具有高级功能的注重隐私的搜索引擎
    - 需要在`.env`文件中设置`BRAVE_SEARCH_API_KEY`
    - 注册地址：https://brave.com/search/api/

- **Arxiv**：用于学术研究的科学论文搜索
    - 无需API密钥
    - 专为科学和学术论文设计

要配置您首选的搜索引擎，请在`.env`文件中设置`SEARCH_API`变量：

```bash
# 选择一个：tavily, duckduckgo, brave_search, arxiv
SEARCH_API=tavily
```

## 特性

### 核心能力

- 🤖 **LLM集成**
    - 通过[litellm](https://docs.litellm.ai/docs/providers)支持集成大多数模型
    - 支持开源模型如Qwen
    - 兼容OpenAI的API接口
    - 多层LLM系统适用于不同复杂度的任务

### 工具和MCP集成

- 🔍 **搜索和检索**
    - 通过Tavily、Brave Search等进行网络搜索
    - 使用Jina进行爬取
    - 高级内容提取

- 🔗 **MCP无缝集成**
    - 扩展私有域访问、知识图谱、网页浏览等能力
    - 促进多样化研究工具和方法的集成

### 人机协作

- 🧠 **人在环中**
    - 支持使用自然语言交互式修改研究计划
    - 支持自动接受研究计划

- 📝 **报告后期编辑**
    - 支持类Notion的块编辑
    - 允许AI优化，包括AI辅助润色、句子缩短和扩展
    - 由[tiptap](https://tiptap.dev/)提供支持

### 内容创作

- 🎙️ **播客和演示文稿生成**
    - AI驱动的播客脚本生成和音频合成
    - 自动创建简单的PowerPoint演示文稿
    - 可定制模板以满足个性化内容需求


## 架构

RearcherNexus实现了一个模块化的多智能体系统架构，专为自动化研究和代码分析而设计。该系统基于LangGraph构建，实现了灵活的基于状态的工作流，其中组件通过定义良好的消息传递系统进行通信。

![架构图](./assets/architecture.png)



系统采用了精简的工作流程，包含以下组件：

1. **协调器**：管理工作流生命周期的入口点
   - 根据用户输入启动研究过程
   - 在适当时候将任务委派给规划器
   - 作为用户和系统之间的主要接口

2. **规划器**：负责任务分解和规划的战略组件
   - 分析研究目标并创建结构化执行计划
   - 确定是否有足够的上下文或是否需要更多研究
   - 管理研究流程并决定何时生成最终报告

3. **研究团队**：执行计划的专业智能体集合：
   - **研究员**：使用网络搜索引擎、爬虫甚至MCP服务等工具进行网络搜索和信息收集。
   - **编码员**：使用Python REPL工具处理代码分析、执行和技术任务。
   每个智能体都可以访问针对其角色优化的特定工具，并在LangGraph框架内运行

4. **报告员**：研究输出的最终阶段处理器
   - 汇总研究团队的发现
   
   - 处理和组织收集的信息
   
   - 生成全面的研究报告
   
     ![架构图](./assets/architecture2.png)

# 文件夹结构

```
ResearcherNexus/
├── src/                     # 核心源代码目录
│   ├── agents/              # 代理定义和实现
│   ├── config/              # 配置管理
│   ├── crawler/             # 网页爬取功能
│   ├── graph/               # LangGraph工作流定义
│   ├── llms/                # 语言模型集成
│   ├── podcast/             # 播客生成功能
│   ├── ppt/                 # 演示文稿生成
│   ├── prompts/             # 提示模板
│   ├── prose/               # 文本处理功能
│   ├── server/              # 服务器实现
│   ├── tools/               # 工具集成(搜索、爬取、代码执行)
│   └── utils/               # 通用工具函数
├── web/                     # Web UI实现(基于Next.js)
│   ├── src/                 # Web UI源代码
│   ├── public/              # 静态资源
├── examples/                # 示例研究报告
├── tests/                   # 测试代码
├── docs/                    # 文档
└── assets/                  # 资源文件
```



## 文本转语音集成

ResarcherNexus现在包含一个文本转语音(TTS)功能，允许您将研究报告转换为语音。此功能使用火山引擎TTS API生成高质量的文本音频。速度、音量和音调等特性也可以自定义。

### 使用TTS API

您可以通过`/api/tts`端点访问TTS功能：

```bash
# 使用curl的API调用示例
curl --location 'http://localhost:8000/api/tts' \
--header 'Content-Type: application/json' \
--data '{
    "text": "这是文本转语音功能的测试。",
    "speed_ratio": 1.0,
    "volume_ratio": 1.0,
    "pitch_ratio": 1.0
}' \
--output speech.mp3
```


## 开发

### 测试

运行测试套件：

```bash
# 运行所有测试
make test

# 运行特定测试文件
pytest tests/integration/test_workflow.py

# 运行覆盖率测试
make coverage
```

### 代码质量

```bash
# 运行代码检查
make lint

# 格式化代码
make format
```

### 使用LangGraph Studio进行调试

ResarcherNexus使用LangGraph作为其工作流架构。您可以使用LangGraph Studio实时调试和可视化工作流。

#### 本地运行LangGraph Studio

RearcherNexus包含一个`langgraph.json`配置文件，该文件定义了LangGraph Studio的图结构和依赖关系。该文件指向项目中定义的工作流图，并自动从`.env`文件加载环境变量。

##### Mac

```bash
# 如果您没有uv包管理器，请安装它
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖并启动LangGraph服务器
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking
```

##### Windows / Linux

```bash
# 安装依赖
pip install -e .
pip install -U "langgraph-cli[inmem]"

# 启动LangGraph服务器
langgraph dev
```

启动LangGraph服务器后，您将在终端中看到几个URL：
- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API文档: http://127.0.0.1:2024/docs

在浏览器中打开Studio UI链接以访问调试界面。

#### 使用LangGraph Studio

在Studio UI中，您可以：

1. 可视化工作流图并查看组件如何连接
2. 实时跟踪执行情况，了解数据如何在系统中流动
3. 检查工作流每个步骤的状态
4. 通过检查每个组件的输入和输出来调试问题
5. 在规划阶段提供反馈以完善研究计划

当您在Studio UI中提交研究主题时，您将能够看到整个工作流执行过程，包括：
- 创建研究计划的规划阶段
- 可以修改计划的反馈循环
- 每个部分的研究和写作阶段
- 最终报告生成

## 示例

以下示例展示了RearcherNexus的功能：

### 研究报告

1. **OpenAI Sora报告** - OpenAI的Sora AI工具分析
   - 讨论功能、访问方式、提示工程、限制和伦理考虑
   - [查看完整报告](examples/openai_sora_report.md)

2. **Google的Agent to Agent协议报告** - Google的Agent to Agent (A2A)协议概述
   - 讨论其在AI智能体通信中的作用及其与Anthropic的Model Context Protocol (MCP)的关系
   - [查看完整报告](examples/what_is_agent_to_agent_protocol.md)

3. **什么是MCP？** - 对"MCP"一词在多个上下文中的全面分析
   - 探讨AI中的Model Context Protocol、化学中的Monocalcium Phosphate和电子学中的Micro-channel Plate
   - [查看完整报告](examples/what_is_mcp.md)

4. **比特币价格波动** - 最近比特币价格走势分析
   - 研究市场趋势、监管影响和技术指标
   - 基于历史数据提供建议
   - [查看完整报告](examples/bitcoin_price_fluctuation.md)

5. **什么是LLM？** - 对大型语言模型的深入探索
   - 讨论架构、训练、应用和伦理考虑
   - [查看完整报告](examples/what_is_llm.md)

6. **如何使用Claude进行深度研究？** - 在深度研究中使用Claude的最佳实践和工作流程
   - 涵盖提示工程、数据分析和与其他工具的集成
   - [查看完整报告](examples/how_to_use_claude_deep_research.md)

7. **医疗保健中的AI采用：影响因素** - 影响医疗保健中AI采用的因素分析
   - 讨论AI技术、数据质量、伦理考虑、经济评估、组织准备度和数字基础设施
   - [查看完整报告](examples/AI_adoption_in_healthcare.md)

8. **量子计算对密码学的影响** - 量子计算对密码学影响的分析
   - 讨论经典密码学的漏洞、后量子密码学和抗量子密码解决方案
   - [查看完整报告](examples/Quantum_Computing_Impact_on_Cryptography.md)

9. **克里斯蒂亚诺·罗纳尔多的表现亮点** - 克里斯蒂亚诺·罗纳尔多表现亮点的分析
   - 讨论他的职业成就、国际进球和在各种比赛中的表现
   - [查看完整报告](examples/Cristiano_Ronaldo's_Performance_Highlights.md)

要运行这些示例或创建您自己的研究报告，您可以使用以下命令：

```bash
# 使用特定查询运行
uv run main.py "哪些因素正在影响医疗保健中的AI采用？"

# 使用自定义规划参数运行
uv run main.py --max_plan_iterations 3 "量子计算如何影响密码学？"

# 在交互模式下运行，带有内置问题
uv run main.py --interactive

# 或者使用基本交互提示运行
uv run main.py

# 查看所有可用选项
uv run main.py --help
```

### 交互模式

应用程序现在支持带有英文和中文内置问题的交互模式：

1. 启动交互模式：
   ```bash
   uv run main.py --interactive
   ```

2. 选择您偏好的语言（English或中文）

3. 从内置问题列表中选择或选择提出您自己问题的选项

4. 系统将处理您的问题并生成全面的研究报告

### 人在环中

RearcherNexus包含一个人在环中机制，允许您在执行研究计划前审查、编辑和批准：

1. **计划审查**：启用人在环中时，系统将在执行前向您展示生成的研究计划

2. **提供反馈**：您可以：
   - 通过回复`[ACCEPTED]`接受计划
   - 通过提供反馈编辑计划（例如，`[EDIT PLAN] 添加更多关于技术实现的步骤`）
   - 系统将整合您的反馈并生成修订后的计划

3. **自动接受**：您可以启用自动接受以跳过审查过程：
   
- 通过API：在请求中设置`auto_accepted_plan: true`
  
4. **API集成**：使用API时，您可以通过`feedback`参数提供反馈：
   ```json
   {
     "messages": [{"role": "user", "content": "什么是量子计算？"}],
     "thread_id": "my_thread_id",
     "auto_accepted_plan": false,
     "feedback": "[EDIT PLAN] 包含更多关于量子算法的内容"
   }
   ```

### 命令行参数

应用程序支持多个命令行参数来自定义其行为：

- **query**：要处理的研究查询（可以是多个词）
- **--interactive**：以交互模式运行，带有内置问题
- **--max_plan_iterations**：最大规划周期数（默认：1）
- **--max_step_num**：研究计划中的最大步骤数（默认：3）
- **--debug**：启用详细调试日志

## 常见问题

请参阅[FAQ.md](docs/FAQ.md)获取更多详情。

## 许可证

本项目是开源的，遵循[MIT许可证](./LICENSE)。

## 致谢

RearcherNexus建立在开源社区的杰出工作基础之上。我们深深感谢所有使RearcherNexus成为可能的项目和贡献者。诚然，我们站在巨人的肩膀上。

我们要向以下项目表达诚挚的感谢，感谢他们的宝贵贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：他们卓越的框架为我们的LLM交互和链提供动力，实现了无缝集成和功能。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：他们在多智能体编排方面的创新方法对于实现RearcherNexus复杂工作流至关重要。

这些项目展示了开源协作的变革力量，我们很自豪能够在他们的基础上构建。

### 核心贡献者
衷心感谢`RearcherNexus`的核心作者，他们的愿景、热情和奉献使这个项目得以实现：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

您坚定不移的承诺和专业知识是RearcherNexus成功的驱动力。我们很荣幸有您引领这一旅程。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wuxixixi/ResearcherNexus&type=Date)](https://star-history.com/#wuxixixi/ResearcherNexus&Date)

## LangSmith集成

ResearcherNexus 集成了 LangSmith 用于跟踪、监控和调试 LLM 应用。通过 LangSmith，您可以：

- 跟踪所有代理交互和工作流执行
- 分析模型性能和响应
- 调试复杂的多代理交互
- 优化提示和工作流

### 配置 LangSmith

1. 首先在 [LangSmith](https://smith.langchain.com/) 注册并获取 API 密钥
2. 在 `.env` 文件中添加以下配置：

```bash
# LangSmith 配置
LANGCHAIN_API_KEY=your_api_key_here
LANGCHAIN_PROJECT=ResearchNexus
LANGCHAIN_TRACING=true
# 可选配置
# LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
# LANGCHAIN_TAGS=prod,v1,research
```

### 查看和分析跟踪数据

配置完成后，ResearcherNexus 的所有运行都会自动记录到 LangSmith 平台。您可以：

1. 登录 [LangSmith Dashboard](https://smith.langchain.com/projects) 查看您的项目
2. 分析每个代理的性能和交互
3. 查看完整的执行路径和中间结果
4. 提取有用的见解以优化您的研究流程

### 在代码中使用 LangSmith

ResearcherNexus 提供了 `src/utils/langsmith_helper.py` 工具，可以直接在代码中访问 LangSmith 数据：

```python
from src.utils.langsmith_helper import get_recent_runs, get_project_stats

# 获取最近的运行记录
recent_runs = get_recent_runs(days=1, limit=10)

# 获取项目统计信息
stats = get_project_stats(days=7)
print(f"成功率: {stats['success_rate']}%, 平均延迟: {stats['avg_latency']}秒")
```

LangSmith 集成对于开发人员和研究人员了解复杂工作流的行为和性能至关重要，尤其是在处理多代理系统时。
