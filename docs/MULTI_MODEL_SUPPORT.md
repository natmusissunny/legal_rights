# 🤖 多模型支持指南

本项目支持 **6种对话模型** + **2种向量化模型**，用户只需配置一个即可使用！

---

## 📊 模型对比表

### 对话生成模型 (LLM)

| 模型 | 价格 (单次问答) | 优势 | 劣势 | 推荐指数 |
|-----|----------------|------|------|---------|
| **DeepSeek** | ¥0.005 | 💰 最便宜<br>🚀 速度快<br>✅ 质量好 | 新模型，稳定性待观察 | ⭐⭐⭐⭐⭐ |
| **通义千问 Qwen** | ¥0.01 | ✅ 国内稳定<br>🏢 阿里背景<br>📈 成熟 | 价格略高于DeepSeek | ⭐⭐⭐⭐⭐ |
| **智谱AI GLM** | ¥0.005 (flash) | 💰 便宜<br>🔄 可同时用于向量化<br>🇨🇳 国内 | flash版质量略低 | ⭐⭐⭐⭐ |
| **Kimi** | ¥0.03 | 📚 超长文本支持<br>🎯 适合处理长文档 | 价格较高 | ⭐⭐⭐ |
| **元宝 MiniMax** | ¥0.02 | 🇨🇳 国内<br>✅ 稳定 | 需要GroupID配置 | ⭐⭐⭐ |
| **Claude** | $0.013 | 🌟 最高质量<br>🧠 推理能力强 | 💸 贵<br>🚫 需代理 | ⭐⭐⭐⭐ |

### 文本向量化模型 (Embedding)

| 模型 | 价格 (建库一次) | 维度 | 优势 | 推荐指数 |
|-----|----------------|------|------|---------|
| **智谱AI** | ¥0.25 | 1024 | 💰 便宜<br>🇨🇳 国内<br>🔄 可同时用于对话 | ⭐⭐⭐⭐⭐ |
| **OpenAI** | $0.001 | 1536 | ✅ 质量高<br>📏 维度高 | ⭐⭐⭐⭐ |

---

## 🎯 推荐配置方案

### 方案1: 最便宜方案（新手推荐）💰

**成本**: 约 ¥0.01/次问答

```env
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=auto
```

**安装**:
```bash
pip install -e ".[zhipu]"
```

**特点**:
- ✅ 最经济的方案
- ✅ DeepSeek质量好
- ✅ 智谱AI向量化效果不错

---

### 方案2: 国内稳定方案（企业推荐）🚀

**成本**: 约 ¥0.02/次问答

```env
# .env 文件
DASHSCOPE_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=auto
```

**安装**:
```bash
pip install -e ".[all-domestic]"
```

**特点**:
- ✅ 阿里云背景，稳定可靠
- ✅ 通义千问成熟度高
- ✅ 完全国内，无需代理

---

### 方案3: 高质量方案（追求效果）🌟

**成本**: 约 $0.013/次问答

```env
# .env 文件
CLAUDE_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-xxxxx
LLM_MODE=auto
```

**安装**:
```bash
pip install -e .
```

**特点**:
- ✅ Claude推理能力最强
- ✅ OpenAI向量化维度高
- ❌ 需要代理
- ❌ 价格较高

---

### 方案4: 单一模型方案（最简单）🎯

**成本**: 约 ¥0.01/次问答

```env
# .env 文件
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=zhipu
```

**安装**:
```bash
pip install -e ".[zhipu]"
```

**特点**:
- ✅ 只需一个API key
- ✅ 配置最简单
- ✅ 智谱AI同时负责对话和向量化

---

## 📝 详细配置指南

### 1️⃣ DeepSeek (推荐)

**获取API密钥**: https://platform.deepseek.com/

**价格**:
- 输入: ¥1/百万tokens
- 输出: ¥2/百万tokens

**配置**:
```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

**支持模型**:
- `deepseek-chat` (默认)
- `deepseek-coder` (代码专用)

**优势**:
- 💰 最便宜的大模型之一
- 🚀 响应速度快
- ✅ 效果接近GPT-4

---

### 2️⃣ 通义千问 Qwen

**获取API密钥**: https://dashscope.console.aliyun.com/

**价格**:
- `qwen-max`: ¥4/百万tokens
- `qwen-plus`: ¥0.8/百万tokens
- `qwen-turbo`: ¥0.3/百万tokens

**配置**:
```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx
```

**安装**:
```bash
pip install dashscope
```

**优势**:
- ✅ 阿里云官方产品
- ✅ 稳定性高
- 📈 持续迭代更新

---

### 3️⃣ 智谱AI GLM

**获取API密钥**: https://open.bigmodel.cn/

**价格**:
- `glm-4-flash`: ¥1/百万tokens (推荐)
- `glm-4-plus`: ¥50/百万tokens

**配置**:
```env
ZHIPUAI_API_KEY=xxxxxxxxxxxxx.xxxxxxxxxxxxx
```

**安装**:
```bash
pip install zhipuai
```

**特殊说明**:
- ✅ **可同时用于对话和向量化**
- ✅ 一个密钥搞定所有功能
- 💰 glm-4-flash 便宜且效果不错

---

### 4️⃣ Kimi (月之暗面)

**获取API密钥**: https://platform.moonshot.cn/

**价格**:
- `moonshot-v1-8k`: ¥12/百万tokens
- `moonshot-v1-32k`: ¥24/百万tokens
- `moonshot-v1-128k`: ¥60/百万tokens

**配置**:
```env
KIMI_API_KEY=sk-xxxxxxxxxxxxx
```

**优势**:
- 📚 超长上下文（最高128k tokens）
- 🎯 适合处理长文档

---

### 5️⃣ 元宝 MiniMax

**获取API密钥**: https://www.minimaxi.com/

**价格**:
- `abab6.5s-chat`: ¥15/百万tokens

**配置**:
```env
MINIMAX_API_KEY=xxxxxxxxxxxxx
MINIMAX_GROUP_ID=xxxxxxxxxxxxx
```

**特殊说明**:
- ⚠️ 需要同时配置 API Key 和 Group ID
- Group ID 在控制台可以找到

---

### 6️⃣ Claude

**获取API密钥**: https://console.anthropic.com/

**价格**:
- 输入: $3/百万tokens
- 输出: $15/百万tokens

**配置**:
```env
CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**优势**:
- 🌟 业界公认最高质量
- 🧠 推理能力最强
- ❌ 需要代理访问

---

### 向量化模型

#### 智谱AI Embedding (推荐)

**配置**:
```env
ZHIPUAI_API_KEY=xxxxxxxxxxxxx.xxxxxxxxxxxxx
```

**价格**: ¥0.005/千tokens

**优势**:
- 💰 便宜
- 🇨🇳 国内稳定
- 🔄 可复用对话模型的密钥

#### OpenAI Embedding

**配置**:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

**价格**: $0.02/百万tokens

**优势**:
- ✅ 质量高
- 📏 向量维度1536（比智谱AI的1024更高）

---

## 🚀 快速开始

### Step 1: 选择方案

根据上面的对比表选择适合你的方案。

**推荐新手**: 方案1（DeepSeek + 智谱AI）

### Step 2: 获取API密钥

访问对应平台注册并获取API密钥。

### Step 3: 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑配置文件
vi .env
```

填入你的API密钥:
```env
DEEPSEEK_API_KEY=你的密钥
ZHIPUAI_API_KEY=你的密钥
LLM_MODE=auto
```

### Step 4: 安装依赖

```bash
# 基础安装
pip install -e .

# 如果使用通义千问
pip install -e ".[qwen]"

# 如果使用智谱AI
pip install -e ".[zhipu]"

# 如果想装全部国内模型
pip install -e ".[all-domestic]"
```

### Step 5: 验证配置

```bash
# 查看配置状态
python -m legal_rights config

# 测试API连接
python -m legal_rights test
```

### Step 6: 构建知识库

```bash
python -m legal_rights build-kb
```

### Step 7: 开始使用

```bash
# 单次问答
python -m legal_rights ask "公司恶意辞退怎么办？"

# 交互式对话
python -m legal_rights chat
```

---

## 🔧 高级配置

### 手动指定模型

```env
# 强制使用DeepSeek
LLM_MODE=deepseek

# 强制使用通义千问
LLM_MODE=qwen

# 强制使用智谱AI
LLM_MODE=zhipu
```

### 混合配置

可以配置多个模型，系统会自动选择最优组合:

```env
# 配置多个模型
DEEPSEEK_API_KEY=sk-xxxxx
DASHSCOPE_API_KEY=sk-xxxxx
ZHIPUAI_API_KEY=xxxxx.xxxxx

# 自动选择（默认选最便宜的）
LLM_MODE=auto
```

自动选择优先级:
1. DeepSeek (最便宜)
2. 通义千问 Qwen (稳定)
3. 智谱AI GLM
4. Kimi
5. MiniMax
6. Claude (最贵)

---

## 💡 常见问题

### Q1: 我只有一个模型的API key，可以使用吗？

可以！如果使用智谱AI，一个密钥可以同时用于对话和向量化。

```env
ZHIPUAI_API_KEY=xxxxx.xxxxx
LLM_MODE=zhipu
```

### Q2: 不同模型质量差别大吗？

实测效果:
- **Claude** > **通义千问** ≈ **DeepSeek** > **智谱GLM-4** > **智谱GLM-4-flash**

但对于法律问答任务，DeepSeek 和通义千问已经足够好。

### Q3: 可以切换模型吗？

可以！只需修改 `.env` 文件中的 `LLM_MODE` 即可。

**注意**: 切换向量化模型后需要重新构建知识库。

### Q4: 哪个方案最省钱？

**DeepSeek + 智谱AI** 是最便宜的方案，单次问答约 ¥0.01。

### Q5: 我在国外，推荐哪个？

推荐 **Claude + OpenAI** 方案，质量最高。

---

## 📊 成本计算器

### 单次问答成本估算

假设:
- 检索5个文档片段: 约1000 tokens
- 用户问题: 约50 tokens
- AI回答: 约300 tokens

| 方案 | LLM成本 | Embedding成本 | 总计 |
|-----|---------|--------------|------|
| DeepSeek + 智谱AI | ¥0.003 | - | ¥0.003 |
| 通义千问 + 智谱AI | ¥0.005 | - | ¥0.005 |
| 智谱GLM (单一) | ¥0.001 | - | ¥0.001 |
| Claude + OpenAI | $0.005 | - | $0.005 |

### 月度成本（100次问答）

| 方案 | 月度成本 |
|-----|---------|
| DeepSeek + 智谱AI | ¥0.3 |
| 通义千问 + 智谱AI | ¥0.5 |
| 智谱GLM (单一) | ¥0.1 |
| Claude + OpenAI | $0.5 |

---

## 🔗 相关文档

- [快速开始](../QUICK_START.md)
- [环境变量配置](.env.example)
- [FAQ](FAQ.md)

---

**更新日期**: 2026-02-06
**版本**: v1.1.0
