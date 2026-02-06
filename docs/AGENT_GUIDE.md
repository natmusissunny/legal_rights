# 智能问答Agent使用指南

本文档说明如何使用法律维权智能Agent进行问答和对话。

## 📋 前置要求

### 1. API 密钥

Agent需要两个API密钥：

- **Claude API**: 用于问答生成
- **OpenAI API**: 用于文本向量化（检索）

**配置方式**:

在 `.env` 文件中添加：

```env
CLAUDE_API_KEY=sk-ant-api03-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

### 2. 向量索引

Agent需要预先构建的向量索引用于检索相关文档。

```bash
# 构建索引
python scripts/test_vector_index.py
```

## 🤖 基础使用

### 初始化Agent

```python
from legal_rights.agent import LegalAgent

# 初始化（自动加载索引）
agent = LegalAgent()
```

### 单次问答

```python
# 提问
answer = agent.ask("如何计算N+1经济补偿金？")

# 显示答案
print(answer.display())

# 访问答案属性
print(f"问题类型: {answer.question_type.value}")
print(f"置信度: {answer.confidence:.2%}")
print(f"相关文档数: {len(answer.relevant_docs)}")
print(f"来源: {answer.sources}")
```

### 多轮对话

```python
# 第一轮
answer1 = agent.chat("我在公司工作了3年被辞退了")
print(answer1.answer_text)

# 第二轮（自动带上下文）
answer2 = agent.chat("公司说是因为业绩不好")
print(answer2.answer_text)

# 第三轮
answer3 = agent.chat("我应该能拿到多少补偿？")
print(answer3.answer_text)

# 查看对话摘要
summary = agent.get_conversation_summary()
print(summary)

# 重置对话
agent.reset_conversation()
```

## 🎯 问题类型

Agent自动识别6种问题类型：

### 1. 经济补偿 (COMPENSATION)

询问是否应该获得补偿、补偿条件等。

**示例**:
- "被公司辞退应该有补偿吗？"
- "什么情况下可以获得经济补偿？"

### 2. 赔偿计算 (CALCULATION)

需要计算具体金额。

**示例**:
- "工作5年月薪10000元，N+1补偿是多少？"
- "如何计算2N赔偿金？"

### 3. 维权流程 (PROCEDURE)

询问维权步骤和流程。

**示例**:
- "被辞退不给补偿怎么办？"
- "劳动仲裁需要什么材料？"

### 4. 法律依据 (LEGAL_BASIS)

询问相关法律条文。

**示例**:
- "经济补偿的法律依据是什么？"
- "劳动法第几条规定了补偿标准？"

### 5. 案例分析 (CASE_ANALYSIS)

询问类似案例。

**示例**:
- "有类似的案例吗？"
- "这种情况法院怎么判？"

### 6. 一般咨询 (GENERAL)

其他一般性问题。

## 🔧 高级功能

### 自定义检索参数

```python
# 检索更多文档
answer = agent.ask(
    question="经济补偿标准",
    top_k=10  # 检索10个文档（默认5个）
)

# 不使用对话上下文
answer = agent.ask(
    question="新问题",
    use_context=False  # 忽略之前的对话
)
```

### 手动分类问题

```python
from legal_rights.models import QuestionType

# 手动指定问题类型
answer = agent.ask(
    question="我的补偿金",
    question_type=QuestionType.CALCULATION
)
```

### 流式输出

```python
from legal_rights.agent import ClaudeClient

client = ClaudeClient()

for chunk in client.stream_complete(
    prompt="请解释经济补偿金",
    system="你是劳动法律师"
):
    print(chunk, end="", flush=True)
```

### 访问对话历史

```python
# 获取最近3轮对话
recent_turns = agent.conversation.get_recent_turns(3)

for turn in recent_turns:
    print(f"Q: {turn.question}")
    print(f"A: {turn.answer.answer_text[:100]}...")
    print()

# 获取完整历史
history = agent.conversation.get_conversation_history()
# 返回: [(question1, answer1), (question2, answer2), ...]
```

### 提取用户信息

```python
# 设置用户信息
agent.conversation.set_user_info("work_years", 3)
agent.conversation.set_user_info("monthly_salary", 8000)

# 获取用户信息
work_years = agent.conversation.get_user_info("work_years")

# 自动提取信息
situation = agent.conversation.extract_user_situation()
print(situation)
# {'work_years': 3, 'monthly_salary': 8000, ...}
```

## 📊 答案对象

### Answer 属性

```python
answer = agent.ask("问题")

# 基本信息
answer.question         # 原始问题
answer.answer_text      # 答案文本
answer.question_type    # 问题类型枚举
answer.confidence       # 置信度 (0-1)
answer.created_at       # 创建时间

# 检索信息
answer.relevant_docs    # 相关文档列表
answer.sources          # 来源URL列表

# 格式化显示
print(answer.display())  # 美化输出
```

### Document 属性

```python
for doc in answer.relevant_docs:
    print(f"ID: {doc.id}")
    print(f"章节: {doc.section_title}")
    print(f"内容: {doc.content}")
    print(f"来源: {doc.source_url}")
    print(f"元数据: {doc.metadata}")
```

## ⚙️ 配置参数

在 `config.py` 或 `.env` 中配置：

```python
# Claude配置
CLAUDE_MODEL = "claude-3-5-sonnet-20240620"  # 模型版本
MAX_TOKENS = 2000                             # 最大生成长度

# 检索配置
TOP_K_RESULTS = 5         # 默认检索文档数
CHUNK_SIZE = 512          # 文档分块大小
CHUNK_OVERLAP = 50        # 分块重叠

# 速率限制
RATE_LIMIT_PER_SECOND = 4  # 每秒请求数
```

### 可选模型

```python
# 更高质量（成本更高）
CLAUDE_MODEL = "claude-3-opus-20240229"

# 更快速度（成本更低）
CLAUDE_MODEL = "claude-3-haiku-20240307"

# 默认（平衡）
CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
```

## 💰 成本估算

### Claude API 定价

| 模型 | Input | Output |
|------|-------|--------|
| Claude 3.5 Sonnet | $3/1M tokens | $15/1M tokens |
| Claude 3 Opus | $15/1M tokens | $75/1M tokens |
| Claude 3 Haiku | $0.25/1M tokens | $1.25/1M tokens |

### 单次问答成本

假设：
- 输入: 2000 tokens（问题 + 检索上下文）
- 输出: 500 tokens

**Sonnet**: $3 × 0.002 + $15 × 0.0005 = **$0.0135** ≈ 1.35 分

### 月度成本（100次问答）

- Sonnet: $1.35
- Haiku: $0.075
- Opus: $7.5

## 🔧 故障排除

### 问题1: "Claude API key is required"

**解决**: 配置 `.env` 文件中的 `CLAUDE_API_KEY`

### 问题2: "Index not found"

**原因**: 向量索引未构建

**解决**:
```bash
python scripts/test_vector_index.py
```

### 问题3: 答案质量不佳

**可能原因**:
1. 检索结果不相关
2. 知识库内容不足
3. 问题表达不清

**解决**:
1. 增加 `top_k` 参数
2. 扩充知识库
3. 重新表述问题
4. 使用更高质量的模型（Opus）

### 问题4: API调用失败

**可能原因**:
- 网络问题
- API密钥无效
- 速率限制

**解决**:
1. 检查网络连接
2. 验证API密钥
3. 降低 `RATE_LIMIT_PER_SECOND`

### 问题5: 置信度过低

**原因**: 检索到的文档相关性不高

**解决**:
1. 重新表述问题
2. 使用关键词辅助检索
3. 检查知识库内容

## 🚀 最佳实践

### 1. 问题表述

**好的问题**:
- "我工作了3年被公司辞退，月薪8000元，应该赔多少？"
- "劳动仲裁需要准备哪些材料？"

**不好的问题**:
- "补偿" （太简短）
- "我的情况" （缺乏上下文）

### 2. 多轮对话

**利用上下文**:
```python
# 第一轮：建立背景
agent.chat("我在公司工作了5年")

# 第二轮：补充信息
agent.chat("月薪12000元")

# 第三轮：具体问题
agent.chat("被辞退应该赔多少？")
```

### 3. 验证答案

始终：
1. 检查 `answer.confidence` 置信度
2. 查看 `answer.sources` 来源
3. 阅读 `answer.relevant_docs` 原文
4. 重要决策前咨询律师

### 4. 性能优化

```python
# 缓存Agent实例
agent = LegalAgent()

# 批量问答时复用
for question in questions:
    answer = agent.ask(question, use_context=False)
    process(answer)
```

## 📚 示例场景

### 场景1: 计算补偿金

```python
agent = LegalAgent()

# 提供完整信息
answer = agent.ask("""
我在公司工作了3年6个月，月平均工资8000元。
公司突然通知我明天就不用来了，理由是经济困难要裁员。
我应该拿到多少补偿？
""")

print(answer.display())
```

### 场景2: 维权指导

```python
agent = LegalAgent()

# 多轮对话了解情况
agent.chat("公司辞退我不给补偿")
agent.chat("理由是说我违反了公司制度")
agent.chat("但我觉得这个理由不成立")
answer = agent.chat("我应该怎么办？")

print(answer.answer_text)
```

### 场景3: 法律条文查询

```python
agent = LegalAgent()

answer = agent.ask("""
经济补偿金的计算标准在劳动法哪一条？
具体是怎么规定的？
""")

print(answer.display())
```

## 🔗 相关文档

- [向量索引使用指南](VECTOR_INDEX_GUIDE.md)
- [配置指南](SETUP_GUIDE.md)
- [项目架构](ARCHITECTURE.md)

---

**版本**: 1.0
**更新日期**: 2026-02-06
