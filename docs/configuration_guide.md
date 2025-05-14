# 安装向导

## 快速安装

Copy the `conf.yaml.example` file to `conf.yaml` and modify the configurations to match your specific settings and requirements.

```bash
cd ResearcherNexus
cp conf.yaml.example conf.yaml
```

## ResearcherNexus支持哪些模型?

在ResearcherNexus中，目前我们仅支持非推理模型，这意味着像 OpenAI 的 o1/o3 或 DeepSeek 的 R1 等模型暂不支持，但我们未来会增加对它们的支持。

### 支持模型

`doubao-1.5-pro-32k-250115`, `gpt-4o`, `qwen-max-latest`, `gemini-2.0-flash`, `deepseek-v3`，并且从理论上来说，任何其他实现 OpenAI API 规范的非推理聊天模型也是如此。

> 【!注意】
> 深度研究过程要求模型具有更长的上下文窗口，并非所有模型都支持。
> 一个解决方法是在网页右上角的设置对话框中将研究计划的最大步骤设置为 2，
> 或者在调用 API 时将 max_step_num 设置为 2。

### 如何切换模型?
您可以通过使用  [litellm format](https://docs.litellm.ai/docs/providers/openai_compatible)的配置修改项目根目录中的`conf.yaml` 文件来切换正在使用的模型。

---

### 如何使用 OpenAI 兼容模型？

ResearcherNexus 支持与 OpenAI 兼容模型的集成，这些模型是实现 OpenAI API 规范的模型。这包括提供与 OpenAI 格式兼容的 API 端点的各种开源和商业模型。您可以参考 [litellm OpenAI-Compatible](https://docs.litellm.ai/docs/providers/openai_compatible) 了解详细的留档。

以下是使用 OpenAI-Compatible 模型的`conf.yaml` 配置示例：

```yaml
# 通过火山引擎使用豆包模型的示例
BASIC_MODEL:
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  model: "doubao-1.5-pro-32k-250115"
  api_key: YOUR_API_KEY

# 阿里云模型示例
BASIC_MODEL:
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-max-latest"
  api_key: YOUR_API_KEY

# deepseek官方模型示例
BASIC_MODEL:
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"
  api_key: YOU_API_KEY

# 使用OpenAI兼容界面的Google gemini模型示例
BASIC_MODEL:
  base_url: "https://generativelanguage.googleapis.com/v1beta/openai/"
  model: "gemini-2.0-flash"
  api_key: YOUR_API_KEY
```

### 如何使用 Ollama 模型？

ResearcherNexus supports the integration of Ollama models. You can refer to [litellm Ollama](https://docs.litellm.ai/docs/providers/ollama). <br>
The following is a configuration example of `conf.yaml` for using Ollama models:

```yaml
BASIC_MODEL:
  model: "ollama/ollama-model-name"
  base_url: "http://localhost:11434" # Local service address of Ollama, which can be started/viewed via ollama serve
```

### How to use OpenRouter models?

ResearcherNexus supports the integration of OpenRouter models. You can refer to [litellm OpenRouter](https://docs.litellm.ai/docs/providers/openrouter). To use OpenRouter models, you need to:
1. Obtain the OPENROUTER_API_KEY from OpenRouter (https://openrouter.ai/) and set it in the environment variable.
2. Add the `openrouter/` prefix before the model name.
3. Configure the correct OpenRouter base URL.

The following is a configuration example for using OpenRouter models:
1. Configure OPENROUTER_API_KEY in the environment variable (such as the `.env` file)
```ini
OPENROUTER_API_KEY=""
```
2. Set the model name in `conf.yaml`
```yaml
BASIC_MODEL:
  model: "openrouter/google/palm-2-chat-bison"
```

Note: The available models and their exact names may change over time. Please verify the currently available models and their correct identifiers in [OpenRouter's official documentation](https://openrouter.ai/docs).

### How to use Azure models?

ResearcherNexus supports the integration of Azure models. You can refer to [litellm Azure](https://docs.litellm.ai/docs/providers/azure). Configuration example of `conf.yaml`:
```yaml
BASIC_MODEL:
  model: "azure/gpt-4o-2024-08-06"
  api_base: $AZURE_API_BASE
  api_version: $AZURE_API_VERSION
  api_key: $AZURE_API_KEY
```
