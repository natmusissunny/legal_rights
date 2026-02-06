# API 使用指南

本文档详细说明法律维权智能助手使用的外部API，包括配置、调用、成本估算和最佳实践。

## 📋 目录

- [API概览](#api概览)
- [Claude API](#claude-api)
- [OpenAI API](#openai-api)
- [成本分析](#成本分析)
- [最佳实践](#最佳实践)
- [错误处理](#错误处理)
- [常见问题](#常见问题)

## API概览

本项目使用两个API服务：

| API | 用途 | 模型 | 价格 |
|-----|------|------|------|
| **Claude API** | 问答生成 | claude-3-5-sonnet-20240620 | $3/1M input<br>$15/1M output |
| **OpenAI API** | 文本向量化 | text-embedding-3-small | $0.02/1M tokens |

## Claude API

### 简介

Claude是Anthropic开发的大语言模型，擅长长文本理解和复杂推理，特别适合法律问答场景。

**官方文档**: https://docs.anthropic.com/

### 获取API密钥

#### 步骤1: 注册账号

访问 [Anthropic Console](https://console.anthropic.com/)

#### 步骤2: 创建API密钥

1. 登录控制台
2. 点击 "API Keys" → "Create Key"
3. 命名（例如：legal_rights_project）
4. 复制密钥（只显示一次）

#### 步骤3: 充值

- 最低充值: $5
- 建议首次充值: $10（可用很久）
- 充值页面: https://console.anthropic.com/settings/billing

### 配置

在 `.env` 文件中配置：

```env
CLAUDE_API_KEY=sk-ant-api03-your-actual-key-here
```

### 使用的模型

**claude-3-5-sonnet-20240620**

- **特点**:
  - 推理能力强，适合复杂法律问答
  - 支持中文，理解准确
  - 200K上下文窗口
  - 响应速度适中

- **定价**:
  - Input: $3/1M tokens
  - Output: $15/1M tokens

- **备选模型**:
  - `claude-3-opus-20240229`: 最高质量，成本更高 ($15/$75)
  - `claude-3-haiku-20240307`: 最快速度，成本最低 ($0.25/$1.25)

### API调用示例

#### 基础调用

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-api03-...")

response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=2000,
    temperature=0.7,
    system="你是一位专业的劳动法律师...",
    messages=[
        {"role": "user", "content": "公司恶意辞退不给补偿怎么办？"}
    ]
)

answer = response.content[0].text
print(answer)
```

#### 流式输出

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20240620",
    max_tokens=2000,
    messages=[
        {"role": "user", "content": "问题"}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Token计算

**估算规则**:
- 中文: 1个字符 ≈ 1-2 tokens
- 英文: 1个单词 ≈ 1.3 tokens

**示例**:
```python
# 输入 (~1000 tokens)
system_prompt = "你是劳动法律师..." (200 tokens)
retrieved_docs = "相关法律条文..." (600 tokens)
user_question = "公司恶意辞退..." (200 tokens)

# 输出 (~500 tokens)
answer = "根据劳动法..." (500 tokens)

# 成本计算
input_cost = 1000 / 1_000_000 * 3 = $0.003
output_cost = 500 / 1_000_000 * 15 = $0.0075
total_cost = $0.0105 ≈ $0.01
```

### 速率限制

**默认限制** (根据账户等级):
- Tier 1 (新用户): 50 requests/min, 40K tokens/min
- Tier 2 ($5+): 1000 requests/min, 80K tokens/min
- Tier 3 ($100+): 2000 requests/min, 160K tokens/min

**项目配置**:
```env
RATE_LIMIT_PER_SECOND=4  # 每秒4次，远低于限制
```

### 错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | API密钥无效 | 检查密钥是否正确 |
| 429 | 速率限制 | 降低请求频率 |
| 500 | 服务器错误 | 重试 |
| 529 | 过载 | 稍后重试 |

## OpenAI API

### 简介

OpenAI提供高质量的文本向量化服务（Embedding），用于语义检索。

**官方文档**: https://platform.openai.com/docs/api-reference

### 获取API密钥

#### 步骤1: 注册账号

访问 [OpenAI Platform](https://platform.openai.com/)

#### 步骤2: 创建API密钥

1. 登录平台
2. 点击头像 → "View API keys"
3. 点击 "Create new secret key"
4. 命名并复制密钥

#### 步骤3: 充值

- 最低充值: $5
- 建议首次充值: $5（Embedding成本极低）
- 充值页面: https://platform.openai.com/account/billing

### 配置

在 `.env` 文件中配置：

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 使用的模型

**text-embedding-3-small**

- **特点**:
  - 1536维向量
  - 性价比高
  - 多语言支持
  - 最大8191 tokens/请求

- **定价**:
  - $0.02/1M tokens

- **备选模型**:
  - `text-embedding-3-large`: 3072维，精度更高 ($0.13/1M)
  - `text-embedding-ada-002`: 旧版模型 ($0.10/1M)

### API调用示例

#### 单条文本

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="公司恶意辞退不给补偿怎么办？"
)

embedding = response.data[0].embedding  # 1536维向量
print(f"向量维度: {len(embedding)}")
```

#### 批量文本

```python
texts = [
    "文本1...",
    "文本2...",
    # ... 最多8191 tokens
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embeddings = [item.embedding for item in response.data]
```

### Token计算

**估算规则**:
- 中文: 1个字符 ≈ 1-2 tokens
- 英文: 1个单词 ≈ 1.3 tokens

**示例**:
```python
# 单次embedding
text = "公司恶意辞退不给补偿怎么办？" (15字 ≈ 20 tokens)
cost = 20 / 1_000_000 * 0.02 = $0.0000004

# 构建知识库 (100个文档，平均500字/文档)
total_tokens = 100 * 500 * 1.5 = 75,000 tokens
cost = 75,000 / 1_000_000 * 0.02 = $0.0015

# 结论: Embedding成本极低，可忽略不计
```

### 速率限制

**默认限制** (Tier 1):
- 3 requests/min
- 150K tokens/min

**优化策略**:
- 批量调用（一次最多2048条）
- 添加缓存机制
- 速率限制 (4次/秒)

### 错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 400 | 输入格式错误 | 检查文本格式 |
| 401 | API密钥无效 | 检查密钥 |
| 429 | 速率限制/余额不足 | 降低频率/充值 |
| 500 | 服务器错误 | 重试 |

## 成本分析

### 知识库构建成本

**一次性成本** (假设100个文档，平均500字/文档):

```
Embedding成本:
- 文档数: 100
- 平均长度: 500字
- 总tokens: 100 * 500 * 1.5 = 75,000 tokens
- 成本: 75,000 / 1,000,000 * $0.02 = $0.0015

总成本: < $0.01
```

### 单次问答成本

**典型场景**:

```
Input (Claude):
- System Prompt: 200 tokens
- Retrieved Docs: 5个 * 200 tokens = 1000 tokens
- User Question: 50 tokens
- 总计: 1250 tokens
- 成本: 1250 / 1,000,000 * $3 = $0.00375

Output (Claude):
- Answer: 500 tokens
- 成本: 500 / 1,000,000 * $15 = $0.0075

Embedding (OpenAI):
- Query: 50 tokens
- 成本: 50 / 1,000,000 * $0.02 ≈ $0.000001

单次总成本: $0.00375 + $0.0075 + $0.000001 ≈ $0.011
```

### 月度/年度成本

**月度成本** (100次问答):
```
100次 * $0.011 = $1.10 ≈ $1.5
```

**年度成本** (1200次问答):
```
1200次 * $0.011 = $13.20 ≈ $15-18
```

### 成本优化建议

1. **使用缓存**: 相同问题不重复调用API
2. **批量处理**: Embedding批量调用
3. **减少检索数量**: Top-K从5降到3
4. **压缩Prompt**: 优化System Prompt长度
5. **选择合适模型**: 简单问题可用Haiku

## 最佳实践

### 1. Prompt优化

**好的Prompt**:
```python
system_prompt = """你是一位专业的劳动法律师，专注于离职维权咨询。

请根据以下法律条文回答用户问题：
{retrieved_docs}

回答要求：
1. 准确引用法律依据
2. 给出具体可操作的建议
3. 使用通俗易懂的语言
4. 保持专业客观的态度
"""
```

**坏的Prompt**:
```python
system_prompt = "你是律师，回答问题。"
```

### 2. 错误重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_claude_api(prompt: str):
    return client.messages.create(...)
```

### 3. 超时设置

```python
client = Anthropic(
    api_key=api_key,
    timeout=30.0  # 30秒超时
)
```

### 4. 速率限制

```python
import time

class RateLimiter:
    def __init__(self, calls_per_second: int):
        self.calls_per_second = calls_per_second
        self.last_call = 0

    def wait_if_needed(self):
        now = time.time()
        elapsed = now - self.last_call
        min_interval = 1.0 / self.calls_per_second

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_call = time.time()

limiter = RateLimiter(calls_per_second=4)

def call_api():
    limiter.wait_if_needed()
    # 调用API
```

### 5. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

def call_api_with_logging(prompt: str):
    logger.info(f"调用Claude API, prompt长度: {len(prompt)}")

    try:
        response = client.messages.create(...)
        logger.info(f"API调用成功, tokens: {response.usage.total_tokens}")
        return response
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        raise
```

## 错误处理

### Claude API错误

```python
from anthropic import APIError, RateLimitError, AuthenticationError

try:
    response = client.messages.create(...)
except AuthenticationError:
    print("❌ API密钥无效，请检查CLAUDE_API_KEY")
except RateLimitError:
    print("⚠️  达到速率限制，请稍后重试")
    time.sleep(60)
except APIError as e:
    print(f"❌ API错误: {e}")
```

### OpenAI API错误

```python
from openai import OpenAIError, RateLimitError, AuthenticationError

try:
    response = client.embeddings.create(...)
except AuthenticationError:
    print("❌ API密钥无效，请检查OPENAI_API_KEY")
except RateLimitError:
    print("⚠️  达到速率限制或余额不足")
except OpenAIError as e:
    print(f"❌ API错误: {e}")
```

### 通用错误处理

```python
def safe_api_call(func, *args, **kwargs):
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                print(f"速率限制，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"错误: {e}, 重试中...")
                time.sleep(1)
            else:
                raise
```

## 常见问题

### Q1: Claude API返回401错误

**原因**: API密钥无效或已过期

**解决**:
1. 检查`.env`文件中的`CLAUDE_API_KEY`是否正确
2. 确认密钥没有多余的空格或换行
3. 在Anthropic Console验证密钥状态
4. 检查账户余额是否充足

### Q2: OpenAI API返回429错误

**原因**: 达到速率限制或余额不足

**解决**:
1. 降低`RATE_LIMIT_PER_SECOND`参数
2. 检查账户余额
3. 升级到更高的Tier
4. 使用批量API减少请求次数

### Q3: 如何查看API使用量？

**Claude**:
访问 https://console.anthropic.com/settings/usage

**OpenAI**:
访问 https://platform.openai.com/usage

### Q4: 如何降低成本？

1. **使用缓存**: 避免重复问题
2. **优化检索**: 减少Top-K数量
3. **压缩Prompt**: 移除冗余内容
4. **选择模型**: 简单任务用Haiku
5. **批量处理**: 减少API调用次数

### Q5: API调用很慢怎么办？

**可能原因**:
- 网络延迟
- 模型负载高
- Token数量大

**优化方案**:
1. 使用流式输出提升体验
2. 减少输入Token数量
3. 选择更快的模型（Haiku）
4. 添加超时和重试机制

### Q6: 如何测试API连接？

```bash
python -m legal_rights test
```

### Q7: 可以在国内使用这些API吗？

**Claude API**: 需要代理

**OpenAI API**: 需要代理

**建议**: 使用稳定的代理服务或VPS

## 参考资源

### Claude

- **官方文档**: https://docs.anthropic.com/
- **Pricing**: https://www.anthropic.com/pricing
- **API Reference**: https://docs.anthropic.com/en/api/messages
- **Examples**: https://github.com/anthropics/anthropic-cookbook

### OpenAI

- **官方文档**: https://platform.openai.com/docs
- **Pricing**: https://openai.com/pricing
- **API Reference**: https://platform.openai.com/docs/api-reference
- **Examples**: https://github.com/openai/openai-cookbook

---

**文档版本**: 1.0
**更新日期**: 2026-02-06
**维护者**: Claude Code
