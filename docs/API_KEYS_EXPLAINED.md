# 🔑 API密钥配置详解

**疑问：到底需要几个API密钥？**

答案：**取决于你选择的模型** - 1个或2个

---

## 🎯 核心概念

本系统需要两种能力：

1. **对话生成 (LLM)** - 用于回答用户问题
2. **文本向量化 (Embedding)** - 用于构建知识库和检索

**不同模型提供的能力不同！**

---

## 📊 模型能力对比表

| 模型 | 对话(LLM) | 向量化(Embedding) | 需要密钥数 | 备注 |
|-----|----------|------------------|-----------|------|
| **智谱AI** | ✅ GLM-4 | ✅ Embedding-2 | **1个** ⭐ | 一个密钥两种能力 |
| 通义千问 Qwen | ✅ Qwen-Max | ❌ | 2个 | 需配合Embedding |
| DeepSeek | ✅ DeepSeek-Chat | ❌ | 2个 | 需配合Embedding |
| Kimi | ✅ Moonshot | ❌ | 2个 | 需配合Embedding |
| 元宝 MiniMax | ✅ Abab | ❌ | 2个 | 需配合Embedding |
| Claude | ✅ Sonnet | ❌ | 2个 | 需配合Embedding |
| OpenAI | ❌ | ✅ text-embedding | 配合LLM | 只做向量化 |

---

## ✅ 方案1: 只需1个密钥（最简单）

### 智谱AI 单一方案

**获取密钥**: https://open.bigmodel.cn/

**.env 配置**:
```env
ZHIPUAI_API_KEY=xxxxxxxxxxxxx.xxxxxxxxxxxxx
LLM_MODE=zhipu
```

**能力**:
- ✅ 对话生成: GLM-4 / GLM-4-Flash
- ✅ 文本向量化: Embedding-2
- ✅ 一个密钥调用两种服务

**成本**: 约 ¥0.01/次问答

**适合人群**:
- ✅ 想要最简单配置的用户
- ✅ 个人学习和小项目
- ✅ 预算有限的用户

**使用示例**:
```bash
# 配置
echo "ZHIPUAI_API_KEY=你的密钥" >> .env
echo "LLM_MODE=zhipu" >> .env

# 安装
pip install zhipuai

# 构建知识库（使用 Embedding-2）
python -m legal_rights build-kb

# 对话问答（使用 GLM-4）
python -m legal_rights ask "问题"
```

---

## ⚠️ 方案2: 需要2个密钥

### 2.1 通义千问 + 智谱AI

**为什么需要2个？**
- 通义千问只提供对话功能
- 必须配合智谱AI或OpenAI做向量化

**.env 配置**:
```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx      # 用于对话
ZHIPUAI_API_KEY=xxxxxxxxxxxxx.xxxxx     # 用于向量化
LLM_MODE=auto
```

**分工**:
- 🗣️ 通义千问: 负责回答问题
- 🔢 智谱AI: 负责文本向量化

**成本**: 约 ¥0.02/次问答

---

### 2.2 DeepSeek + 智谱AI (最便宜)

**.env 配置**:
```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx       # 用于对话
ZHIPUAI_API_KEY=xxxxxxxxxxxxx.xxxxx     # 用于向量化
LLM_MODE=auto
```

**分工**:
- 🗣️ DeepSeek: 负责回答问题（最便宜）
- 🔢 智谱AI: 负责文本向量化

**成本**: 约 ¥0.005/次问答（最便宜方案）

---

### 2.3 Claude + OpenAI (最高质量)

**.env 配置**:
```env
CLAUDE_API_KEY=sk-ant-api03-xxxxx       # 用于对话
OPENAI_API_KEY=sk-xxxxxxxxxxxxx         # 用于向量化
LLM_MODE=auto
```

**分工**:
- 🗣️ Claude: 负责回答问题（质量最高）
- 🔢 OpenAI: 负责文本向量化（维度最高1536）

**成本**: 约 $0.013/次问答

**缺点**:
- ❌ 需要代理访问
- ❌ 成本较高

---

## 🔍 命令使用的API详解

### build-kb 命令

```bash
python -m legal_rights build-kb
```

**使用的API**:
- ✅ Embedding API （文本向量化）
- ❌ 不需要 LLM API

**配置要求**:
```env
# 只需配置以下任一项
ZHIPUAI_API_KEY=xxxxx      # 智谱AI Embedding
# 或
OPENAI_API_KEY=xxxxx       # OpenAI Embedding
```

---

### ask / chat 命令

```bash
python -m legal_rights ask "问题"
python -m legal_rights chat
```

**使用的API**:
- ✅ LLM API （对话生成）
- ✅ Embedding API （检索相关文档）

**配置要求**:

**如果使用智谱AI** - 1个密钥:
```env
ZHIPUAI_API_KEY=xxxxx
LLM_MODE=zhipu
```

**如果使用其他模型** - 2个密钥:
```env
# LLM（任选一个）
DASHSCOPE_API_KEY=xxxxx    # 通义千问
# 或 DEEPSEEK_API_KEY=xxxxx
# 或 KIMI_API_KEY=xxxxx
# 或 CLAUDE_API_KEY=xxxxx

# Embedding（必选一个）
ZHIPUAI_API_KEY=xxxxx      # 智谱AI
# 或 OPENAI_API_KEY=xxxxx

LLM_MODE=auto
```

---

## 💡 常见误区

### ❌ 误区1: "我只配了通义千问，为什么build-kb报错？"

**原因**: 通义千问只提供对话功能，不提供向量化功能

**解决**: 额外配置智谱AI或OpenAI的Embedding
```env
DASHSCOPE_API_KEY=xxxxx         # 已有
ZHIPUAI_API_KEY=xxxxx           # 需要添加
```

---

### ❌ 误区2: "我配了智谱AI，为什么还要我配OpenAI？"

**原因**: 可能代码中有bug，或配置没生效

**解决**:
1. 确认 `.env` 文件在项目根目录
2. 确认配置格式正确
3. 运行 `python -m legal_rights config` 检查

---

### ❌ 误区3: "我有Claude API，为什么build-kb失败？"

**原因**: Claude只提供对话，不提供向量化

**解决**: 额外配置Embedding服务
```env
CLAUDE_API_KEY=xxxxx            # 已有（用于对话）
OPENAI_API_KEY=xxxxx            # 需要添加（用于向量化）
# 或
ZHIPUAI_API_KEY=xxxxx           # 推荐（更便宜）
```

---

## 🎯 推荐配置方案总结

### 场景1: 我想最简单 → 智谱AI

```env
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=zhipu
```

- ✅ 只需1个密钥
- ✅ 配置最简单
- ✅ 国内访问稳定
- 💰 成本: ¥0.01/次

---

### 场景2: 我想最便宜 → DeepSeek + 智谱AI

```env
DEEPSEEK_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=auto
```

- ⚠️ 需要2个密钥
- ✅ 成本最低
- ✅ 质量不错
- 💰 成本: ¥0.005/次

---

### 场景3: 我想最稳定 → 通义千问 + 智谱AI

```env
DASHSCOPE_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=auto
```

- ⚠️ 需要2个密钥
- ✅ 阿里云背景
- ✅ 企业级稳定
- 💰 成本: ¥0.02/次

---

### 场景4: 我想最高质量 → Claude + OpenAI

```env
CLAUDE_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx
LLM_MODE=auto
```

- ⚠️ 需要2个密钥
- ⚠️ 需要代理
- ✅ 质量最高
- 💰 成本: $0.013/次

---

## 🔗 获取API密钥链接

| 服务 | 获取地址 | 提供能力 |
|-----|---------|---------|
| 智谱AI | https://open.bigmodel.cn/ | 对话 + 向量化 |
| 通义千问 | https://dashscope.console.aliyun.com/ | 对话 |
| DeepSeek | https://platform.deepseek.com/ | 对话 |
| Kimi | https://platform.moonshot.cn/ | 对话 |
| 元宝 | https://www.minimaxi.com/ | 对话 |
| Claude | https://console.anthropic.com/ | 对话 |
| OpenAI | https://platform.openai.com/ | 向量化 |

---

## ✅ 验证配置

运行以下命令检查配置:

```bash
python -m legal_rights config
```

**正确的输出示例**（智谱AI单一密钥）:
```
📊 当前配置状态
============================================================

🤖 大语言模型 (LLM):
  ✅ 智谱AI API: xxxxx...xxxxx

🔢 向量化模型 (Embedding):
  ✅ 智谱AI API: xxxxx...xxxxx

🎯 自动选择结果:
  LLM: 智谱AI GLM-4
  Embedding: 智谱AI Embedding-2

✅ 配置验证通过！
```

**正确的输出示例**（双密钥配置）:
```
📊 当前配置状态
============================================================

🤖 大语言模型 (LLM):
  ✅ DeepSeek API: sk-xxxxx...xxxxx

🔢 向量化模型 (Embedding):
  ✅ 智谱AI API: xxxxx...xxxxx

🎯 自动选择结果:
  LLM: DeepSeek
  Embedding: 智谱AI Embedding-2

✅ 配置验证通过！
```

---

## 🆘 还有问题？

查看其他文档:
- [最小配置指南](MINIMAL_SETUP.md) - 快速上手
- [多模型支持详解](MULTI_MODEL_SUPPORT.md) - 所有模型对比
- [常见问题FAQ](FAQ.md) - 问题排查

---

**更新时间**: 2026-02-06
**版本**: v1.1.0
