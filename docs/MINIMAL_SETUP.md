# 🚀 最小配置指南 - 5分钟快速上手

**只需一个API密钥即可运行！**

---

## 📋 需要什么？

### 必需 ✅

1. **Python 3.10+**
2. **API 密钥** - 根据选择的模型：

   **方案A: 只需1个密钥** ⭐ 推荐
   - 智谱AI (同时提供对话和向量化)

   **方案B: 需要2个密钥**
   - 任选一个对话模型：通义千问 / DeepSeek / Kimi / 元宝 / Claude
   - **加上**一个向量化模型：智谱AI / OpenAI

### 不需要 ❌

- ❌ 不需要 Claude API (除非你选择Claude)
- ❌ 不需要 OpenAI API (除非你选择它)
- ❌ 不需要代理 (使用国内模型)
- ❌ 不需要数据库

---

## 🤔 为什么智谱AI只需1个密钥？

**智谱AI特殊之处**：
- ✅ 提供对话功能 (GLM-4)
- ✅ 提供向量化功能 (Embedding-2)
- ✅ 用同一个 API Key 调用两种服务

**其他模型**：
- 通义千问、DeepSeek等只提供对话功能
- 必须额外配置向量化服务 (智谱AI 或 OpenAI)

---

## ⚡ 三种快速方案

### 方案1: 智谱AI单一密钥 (最简单) ⭐⭐⭐⭐⭐

**成本**: ¥0.01/次问答
**优势**: 只需一个密钥，配置最简单

```bash
# Step 1: 获取API密钥
# 访问: https://open.bigmodel.cn/
# 注册并获取 API Key

# Step 2: 克隆项目
git clone https://github.com/YOUR_GITHUB_USERNAME/legal_rights.git
cd legal_rights

# Step 3: 配置环境
cp .env.example .env
echo "ZHIPUAI_API_KEY=你的密钥" >> .env
echo "LLM_MODE=zhipu" >> .env

# Step 4: 安装依赖
pip install -e .
pip install zhipuai

# Step 5: 构建知识库
python -m legal_rights build-kb

# Step 6: 开始使用
python -m legal_rights ask "公司恶意辞退怎么办？"
```

---

### 方案2: DeepSeek + 智谱AI (最便宜) ⭐⭐⭐⭐⭐

**成本**: ¥0.005/次问答
**优势**: 最经济，质量好

```bash
# Step 1: 获取API密钥
# DeepSeek: https://platform.deepseek.com/
# 智谱AI: https://open.bigmodel.cn/

# Step 2: 配置环境
cp .env.example .env
echo "DEEPSEEK_API_KEY=你的DeepSeek密钥" >> .env
echo "ZHIPUAI_API_KEY=你的智谱密钥" >> .env
echo "LLM_MODE=auto" >> .env

# Step 3: 安装依赖
pip install -e .
pip install zhipuai

# Step 4: 构建知识库
python -m legal_rights build-kb

# Step 5: 开始使用
python -m legal_rights ask "N+1补偿怎么计算？"
```

---

### 方案3: 通义千问 + 智谱AI (国内稳定) ⭐⭐⭐⭐⭐

**成本**: ¥0.02/次问答
**优势**: 阿里云背景，企业级稳定

```bash
# Step 1: 获取API密钥
# 通义千问: https://dashscope.console.aliyun.com/
# 智谱AI: https://open.bigmodel.cn/

# Step 2: 配置环境
cp .env.example .env
echo "DASHSCOPE_API_KEY=你的千问密钥" >> .env
echo "ZHIPUAI_API_KEY=你的智谱密钥" >> .env
echo "LLM_MODE=auto" >> .env

# Step 3: 安装依赖
pip install -e .
pip install dashscope zhipuai

# Step 4: 构建知识库
python -m legal_rights build-kb

# Step 5: 开始使用
python -m legal_rights chat  # 交互式对话
```

---

## 🔍 各命令所需的API

| 命令 | 需要的API | 说明 |
|-----|----------|------|
| `build-kb` | Embedding API | 只需向量化API |
| `ask` | LLM + Embedding | 需要两个API |
| `chat` | LLM + Embedding | 需要两个API |
| `config` | 无 | 查看配置状态 |
| `test` | LLM + Embedding | 测试API连接 |

**重要**:
- `build-kb` **不需要**对话模型（LLM）API，只需要 Embedding API
- 如果使用智谱AI，一个密钥可以同时满足两种需求

---

## 🆘 常见错误

### 错误1: "OpenAI API key is required"

**原因**: 运行 `build-kb` 时没有配置 Embedding API

**解决**:
```bash
# 配置智谱AI（推荐）
echo "ZHIPUAI_API_KEY=你的密钥" >> .env

# 或配置 OpenAI
echo "OPENAI_API_KEY=你的密钥" >> .env
```

### 错误2: "未配置任何LLM API密钥"

**原因**: 运行 `ask` 或 `chat` 时没有配置对话模型API

**解决**:
```bash
# 如果已有智谱AI密钥
echo "LLM_MODE=zhipu" >> .env

# 或添加其他模型密钥
echo "DEEPSEEK_API_KEY=你的密钥" >> .env
```

### 错误3: ModuleNotFoundError: No module named 'zhipuai'

**原因**: 使用了智谱AI但没有安装SDK

**解决**:
```bash
pip install zhipuai
```

### 错误4: ModuleNotFoundError: No module named 'dashscope'

**原因**: 使用了通义千问但没有安装SDK

**解决**:
```bash
pip install dashscope
```

---

## 📊 不同方案对比

| 方案 | API数量 | 月度成本(100次) | 配置难度 | 推荐场景 |
|-----|---------|----------------|---------|---------|
| 智谱AI单一 | 1个 | ¥1 | ⭐ 最简单 | 个人用户 |
| DeepSeek+智谱 | 2个 | ¥0.5 | ⭐⭐ 简单 | 预算有限 |
| 千问+智谱 | 2个 | ¥2 | ⭐⭐ 简单 | 企业用户 |

---

## ✅ 验证安装

### 1. 检查配置
```bash
python -m legal_rights config
```

应该看到:
```
✅ Embedding API: zhipu
✅ LLM API: zhipu (或其他)
✅ 配置验证通过！
```

### 2. 测试API连接
```bash
python -m legal_rights test
```

应该看到:
```
✅ LLM API 测试成功
✅ Embedding API 测试成功
```

### 3. 测试问答
```bash
python -m legal_rights ask "测试问题"
```

应该返回答案。

---

## 💡 使用技巧

### 查看帮助
```bash
python -m legal_rights --help
```

### 跳过抓取（使用缓存）
```bash
python -m legal_rights build-kb --skip-scrape
```

### 强制重新抓取
```bash
python -m legal_rights build-kb --force
```

### 交互式对话
```bash
python -m legal_rights chat
```

### 批量问答
创建 `questions.txt`:
```
公司恶意辞退怎么办？
N+1补偿如何计算？
劳动仲裁需要什么材料？
```

然后：
```bash
while read line; do
  python -m legal_rights ask "$line"
done < questions.txt
```

---

## 📚 下一步

- 📖 阅读 [多模型支持指南](MULTI_MODEL_SUPPORT.md) 了解更多模型选择
- 🔧 查看 [FAQ](FAQ.md) 解决常见问题
- 📄 查看 [完整文档](../README.md) 了解所有功能

---

## 🆘 需要帮助？

1. 查看 [FAQ文档](FAQ.md)
2. 查看 [网页抓取问题指南](SCRAPING_ISSUES.md)
3. 提交 Issue: https://github.com/YOUR_GITHUB_USERNAME/legal_rights/issues

---

**更新时间**: 2026-02-06
**适用版本**: v1.1.0+
