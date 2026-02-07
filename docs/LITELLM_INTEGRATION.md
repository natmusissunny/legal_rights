# 🔄 LiteLLM 集成指南

**通过 LiteLLM 统一管理所有大模型**

---

## 🎯 什么是 LiteLLM？

**LiteLLM** = 大模型的"统一接口"

支持 100+ 模型提供商：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- 阿里云（通义千问）
- 智谱AI（GLM）
- DeepSeek
- 更多...

**官方文档**: https://docs.litellm.ai/

---

## 🌟 为什么要用 LiteLLM？

### 对比：不使用 LiteLLM

```python
# 需要为每个模型写适配代码
if model == "claude":
    from anthropic import Anthropic
    client = Anthropic(api_key=key)
    response = client.messages.create(...)

elif model == "qwen":
    from dashscope import Generation
    response = Generation.call(...)

elif model == "deepseek":
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url="...")
    response = client.chat.completions.create(...)
```

### 使用 LiteLLM

```python
# 统一接口，一行代码搞定
from litellm import completion

response = completion(
    model="claude-3-opus",  # 或 gpt-4 / qwen-max
    messages=[{"role": "user", "content": "..."}]
)
```

### LiteLLM 的优势

1. ✅ **统一接口** - 一套代码支持所有模型
2. ✅ **负载均衡** - 自动在多个模型间分配请求
3. ✅ **失败重试** - 自动重试失败的请求
4. ✅ **成本追踪** - 统计每个模型的调用成本
5. ✅ **速率限制** - 避免超过API限额
6. ✅ **模型路由** - 根据规则自动选择模型

---

## 🚀 两种使用方式

### 方式1: 直接使用 LiteLLM（简单）

**适合**: 单机使用，不需要代理服务器

```bash
# 1. 安装
pip install litellm

# 2. 配置 .env
echo "LITELLM_MODEL=claude-3-opus-20240229" >> .env
echo "LLM_MODE=litellm" >> .env

# 同时配置对应模型的API密钥
echo "ANTHROPIC_API_KEY=your-claude-key" >> .env

# 3. 使用
python -m legal_rights ask "问题"
```

### 方式2: 使用 LiteLLM 代理（推荐）

**适合**: 需要负载均衡、成本追踪、多用户等高级功能

```bash
# 1. 安装
pip install 'litellm[proxy]'

# 2. 创建配置文件
cat > litellm_config.yaml << EOF
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: your-openai-key

  - model_name: claude
    litellm_params:
      model: claude-3-opus-20240229
      api_key: your-claude-key

  - model_name: qwen
    litellm_params:
      model: qwen/qwen-max
      api_key: your-qwen-key
EOF

# 3. 启动 LiteLLM 代理
litellm --config litellm_config.yaml --port 4000

# 4. 配置项目
echo "LITELLM_MODEL=gpt-4" >> .env
echo "LITELLM_API_BASE=http://localhost:4000" >> .env
echo "LLM_MODE=litellm" >> .env

# 5. 使用
python -m legal_rights ask "问题"
```

---

## 📝 配置示例

### 示例1: 直接使用 Claude

**.env 文件**:
```env
# 使用 LiteLLM 调用 Claude
LITELLM_MODEL=claude-3-opus-20240229
LLM_MODE=litellm

# Claude API密钥
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Embedding（仍需配置）
ZHIPUAI_API_KEY=xxxxx.xxxxx
```

**原理**:
- LiteLLM 读取 `ANTHROPIC_API_KEY`
- 自动调用 Claude API

---

### 示例2: 使用 LiteLLM 代理

**litellm_config.yaml**:
```yaml
model_list:
  # OpenAI GPT-4
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  # Claude Opus
  - model_name: claude-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

  # 通义千问
  - model_name: qwen
    litellm_params:
      model: qwen/qwen-max
      api_key: os.environ/DASHSCOPE_API_KEY

# 负载均衡配置（可选）
router_settings:
  routing_strategy: simple-shuffle  # 随机选择

# 速率限制（可选）
general_settings:
  max_parallel_requests: 10
```

**启动代理**:
```bash
# 设置环境变量
export OPENAI_API_KEY=sk-xxxxx
export ANTHROPIC_API_KEY=sk-ant-xxxxx
export DASHSCOPE_API_KEY=sk-xxxxx

# 启动
litellm --config litellm_config.yaml --port 4000
```

**.env 文件**:
```env
# 使用 LiteLLM 代理
LITELLM_MODEL=gpt-4
LITELLM_API_BASE=http://localhost:4000
LLM_MODE=litellm

# Embedding
ZHIPUAI_API_KEY=xxxxx.xxxxx
```

---

### 示例3: 负载均衡 + 失败重试

**litellm_config.yaml**:
```yaml
model_list:
  # 主力模型：GPT-4
  - model_name: gpt-4-primary
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  # 备用模型：Claude
  - model_name: gpt-4-fallback
    litellm_params:
      model: claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

# 路由设置
router_settings:
  routing_strategy: usage-based-routing-v2
  num_retries: 3  # 失败重试3次
  timeout: 60     # 超时时间60秒
  fallbacks:
    - gpt-4-primary
    - gpt-4-fallback  # GPT-4失败则用Claude

# 成本追踪
litellm_settings:
  success_callback: ["langfuse"]  # 可选：发送到Langfuse
  failure_callback: ["langfuse"]
```

---

## 🔧 高级功能

### 1. 成本追踪

```yaml
# litellm_config.yaml
litellm_settings:
  success_callback: ["langfuse", "supabase"]

langfuse_params:
  public_key: your-key
  secret_key: your-secret
```

启动后访问: http://localhost:4000/metrics

查看：
- 总请求数
- 成功/失败率
- 每个模型的成本
- 响应时间

### 2. 负载均衡

```yaml
router_settings:
  routing_strategy: least-busy  # 选择最空闲的模型
  # 或
  routing_strategy: simple-shuffle  # 随机选择
  # 或
  routing_strategy: usage-based-routing-v2  # 基于使用量
```

### 3. 模型路由

```yaml
# 根据请求内容选择模型
router_settings:
  model_group_alias:
    "cheap": ["gpt-3.5-turbo", "qwen-turbo"]
    "expensive": ["gpt-4", "claude-3-opus"]

# 使用时指定组
# completion(model="cheap", messages=[...])
```

### 4. 速率限制

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: xxx
      rpm: 60  # 每分钟60次请求
      tpm: 100000  # 每分钟100k tokens
```

---

## 🎯 与现有功能对比

### 不使用 LiteLLM（现有方式）

```env
# 需要配置具体模型的密钥
DEEPSEEK_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=auto
```

**特点**:
- ✅ 简单直接
- ✅ 无需额外服务
- ❌ 每个模型需要单独适配
- ❌ 无法负载均衡
- ❌ 无法成本追踪

### 使用 LiteLLM

```env
# 统一接口
LITELLM_MODEL=gpt-4
LITELLM_API_BASE=http://localhost:4000
LLM_MODE=litellm

# 只需配置 Embedding
ZHIPUAI_API_KEY=xxxxx.xxxxx
```

**特点**:
- ✅ 统一接口
- ✅ 支持负载均衡
- ✅ 支持成本追踪
- ✅ 支持失败重试
- ⚠️ 需要启动代理服务（方式2）

---

## 📊 实际使用场景

### 场景1: 个人开发（直接使用）

```bash
# 安装
pip install litellm

# 配置
cat >> .env << EOF
LITELLM_MODEL=claude-3-opus-20240229
LLM_MODE=litellm
ANTHROPIC_API_KEY=your-key
ZHIPUAI_API_KEY=your-key
EOF

# 使用
python -m legal_rights ask "公司恶意辞退怎么办？"
```

**优势**: 无需启动代理，配置简单

---

### 场景2: 团队协作（使用代理）

```bash
# 1. 服务器上启动 LiteLLM 代理
# server.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: team-openai-key
  - model_name: claude
    litellm_params:
      model: claude-3-opus-20240229
      api_key: team-claude-key

litellm --config server.yaml --port 4000

# 2. 团队成员只需配置代理地址
# .env
LITELLM_MODEL=gpt-4
LITELLM_API_BASE=http://team-server:4000
LLM_MODE=litellm
ZHIPUAI_API_KEY=my-embedding-key
```

**优势**:
- 统一管理API密钥
- 成本追踪和控制
- 负载均衡

---

### 场景3: 混合使用

```bash
# 开发环境：直接调用（便宜）
DEEPSEEK_API_KEY=my-key
LLM_MODE=deepseek

# 生产环境：LiteLLM代理（稳定）
LITELLM_MODEL=gpt-4
LITELLM_API_BASE=http://prod-server:4000
LLM_MODE=litellm
```

**优势**: 灵活切换，开发省钱，生产稳定

---

## 🔍 完整配置示例

### 生产级 LiteLLM 配置

```yaml
# litellm_config.yaml
model_list:
  # 主力：OpenAI
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
      rpm: 500
      tpm: 150000

  # 备用1：Claude
  - model_name: claude-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 400
      tpm: 100000

  # 备用2：通义千问（便宜）
  - model_name: qwen-max
    litellm_params:
      model: qwen/qwen-max
      api_key: os.environ/DASHSCOPE_API_KEY
      rpm: 1000
      tpm: 200000

# 路由策略
router_settings:
  routing_strategy: usage-based-routing-v2
  num_retries: 3
  timeout: 60
  fallbacks:
    - gpt-4
    - claude-opus
    - qwen-max  # 最后降级到便宜模型

# 成本追踪
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]
  set_verbose: true

# 数据库（可选）
general_settings:
  database_url: postgresql://user:pass@localhost/litellm

# UI访问控制（可选）
environment_variables:
  LITELLM_MASTER_KEY: your-secret-key
```

**启动**:
```bash
litellm --config litellm_config.yaml \
  --port 4000 \
  --num_workers 4 \
  --detailed_debug
```

**访问**:
- API: http://localhost:4000
- UI: http://localhost:4000/ui
- Metrics: http://localhost:4000/metrics

---

## 📚 常见问题

### Q1: 必须使用 LiteLLM 吗？

**不必须**。LiteLLM 是可选功能。

- ✅ 使用 LiteLLM：适合需要高级功能的用户
- ✅ 不使用：继续用现有的直接调用方式

### Q2: LiteLLM 会增加延迟吗？

**几乎没有**。LiteLLM 只是一个轻量级代理，延迟增加 < 10ms。

### Q3: 可以同时用 LiteLLM 和直接调用吗？

**可以**。通过 `LLM_MODE` 切换：

```env
# 使用 LiteLLM
LLM_MODE=litellm

# 使用 DeepSeek
LLM_MODE=deepseek
```

### Q4: LiteLLM 支持 Embedding 吗？

**支持**，但本项目的 Embedding 仍使用直接调用方式。

原因：Embedding 调用简单，不需要负载均衡等高级功能。

### Q5: 成本会增加吗？

**不会**。LiteLLM 本身免费开源，只产生模型调用成本。

---

## ✅ 快速开始

### 最简单方式（直接使用）

```bash
# 1. 安装
pip install litellm

# 2. 配置
cat >> .env << EOF
LITELLM_MODEL=claude-3-opus-20240229
LLM_MODE=litellm
ANTHROPIC_API_KEY=your-claude-key
ZHIPUAI_API_KEY=your-zhipu-key
EOF

# 3. 测试
python -m legal_rights config

# 4. 使用
python -m legal_rights ask "测试问题"
```

### 推荐方式（使用代理）

```bash
# 1. 安装
pip install 'litellm[proxy]'

# 2. 创建配置
cat > litellm_config.yaml << 'EOF'
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: your-key
EOF

# 3. 启动代理
litellm --config litellm_config.yaml --port 4000

# 4. 配置项目
cat >> .env << EOF
LITELLM_MODEL=gpt-4
LITELLM_API_BASE=http://localhost:4000
LLM_MODE=litellm
ZHIPUAI_API_KEY=your-zhipu-key
EOF

# 5. 使用
python -m legal_rights ask "测试问题"
```

---

## 🔗 相关资源

- **LiteLLM 官方文档**: https://docs.litellm.ai/
- **支持的模型列表**: https://docs.litellm.ai/docs/providers
- **LiteLLM GitHub**: https://github.com/BerriAI/litellm
- **LiteLLM 代理文档**: https://docs.litellm.ai/docs/proxy/quick_start

---

**更新日期**: 2026-02-06
**版本**: v1.1.0
