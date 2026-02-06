# 🚀 快速开始指南（小白版）

**5分钟部署，立即使用！**

---

## 📋 准备工作

### 需要准备

1. **Python 3.10+**
   - 检查: `python3 --version`
   - 下载: https://www.python.org/downloads/

2. **API 密钥**（二选一）:
   - **方案A (国际版)**: Claude + OpenAI
   - **方案B (国内版，推荐)**: 通义千问 + 智谱AI

### API 密钥获取

**通义千问** (推荐，国内访问快):
1. 访问: https://dashscope.console.aliyun.com/
2. 注册/登录
3. 创建 API Key

**智谱AI** (推荐，配合通义千问):
1. 访问: https://open.bigmodel.cn/
2. 注册/登录
3. 创建 API Key

---

## 🎯 一键安装（推荐）

### Step 1: 下载代码

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/legal_rights.git
cd legal_rights
```

### Step 2: 运行安装脚本

```bash
bash install.sh
```

脚本会自动完成:
- ✅ 检查 Python 环境
- ✅ 安装依赖包
- ✅ 配置 API 密钥
- ✅ 构建知识库

**跟随提示操作即可！**

---

## 📝 手动安装（详细步骤）

如果一键安装失败，按以下步骤手动安装：

### Step 1: 安装依赖

```bash
# 基础依赖
pip3 install -r requirements.txt

# 国内大模型支持（可选）
pip3 install dashscope zhipuai
```

### Step 2: 配置 API 密钥

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
vi .env  # 或使用其他编辑器
```

**.env 文件内容**（选择一个方案）:

**方案A - 国内版（推荐）:**
```env
# 通义千问 API Key
DASHSCOPE_API_KEY=sk-你的密钥

# 智谱AI API Key
ZHIPUAI_API_KEY=你的密钥

# 自动选择模式
LLM_MODE=auto
```

**方案B - 国际版:**
```env
# Claude API Key
CLAUDE_API_KEY=sk-ant-api03-你的密钥

# OpenAI API Key
OPENAI_API_KEY=sk-你的密钥

# 自动选择模式
LLM_MODE=auto
```

### Step 3: 安装命令（可选）

```bash
# 安装到系统，之后可使用 'legal-rights' 命令
pip3 install -e .
```

### Step 4: 验证配置

```bash
# 如果安装了命令
legal-rights config

# 或使用模块方式
python3 -m legal_rights config
```

**预期输出:**
```
📊 当前配置状态
============================================================

🤖 大语言模型 (LLM):
  ✅ 通义千问 API: sk-xxxxx...xxx

🔢 向量化模型 (Embedding):
  ✅ 智谱AI API: xxxxx...

🎯 自动选择结果:
  LLM: 通义千问
  Embedding: 智谱AI

✅ 配置验证通过！
```

### Step 5: 构建知识库

```bash
# 首次使用必须构建知识库
legal-rights build-kb
# 或
python3 -m legal_rights build-kb
```

**过程说明:**
```
🚀 开始构建知识库...

[1/4] 📥 抓取网页内容...
   从 3 个权威法律网站抓取内容
   ✓ 已抓取: 3 个网页

[2/4] 📝 解析文档结构...
   ✓ 解析成功: 15+ 个文档块

[3/4] 🔢 生成向量索引...
   调用 Embedding API 进行向量化
   ✓ 构建 FAISS 索引完成

[4/4] 💾 保存知识库...
   ✓ 保存完成

✅ 知识库构建完成！
```

**耗时**: 3-5 分钟

---

## 💬 开始使用

### 单次问答

```bash
legal-rights ask "公司恶意辞退不给补偿怎么办？"
```

**示例输出:**
```
🤖 正在思考...

📝 回答:

公司恶意辞退不给经济补偿是违法行为，您可以采取以下维权措施:

1. 协商解决
   首先与公司协商，要求支付经济补偿金。

2. 劳动仲裁
   协商无果可向当地劳动仲裁委员会申请仲裁。

3. 经济补偿标准
   N+1 或 2N（具体根据辞退原因）

📚 法律依据:
  • 《劳动合同法》第四十七条
  • 《劳动合同法》第八十七条

🔗 参考来源:
  • https://m12333.cn/qa/myyuf.html
  • https://www.hshfy.sh.cn/...

⚖️  置信度: 85%
```

### 交互式对话

```bash
legal-rights chat
```

**示例对话:**
```
💬 法律维权助手 (输入 'exit' 退出)

你: 我在公司工作了3年，被辞退应该赔多少？
AI: 根据《劳动合同法》，经济补偿按您的工作年限计算...

你: 公司说是因为业绩不好
AI: 如果是因业绩问题辞退，需要符合法定条件...

你: exit
再见！
```

### 查看统计信息

```bash
legal-rights stats
```

**输出示例:**
```
📊 知识库统计信息

总文档数: 37
数据源: 3 个
向量维度: 1024

数据来源:
  • 12333.cn - 政策解读
  • 上海法院 - 司法实践
  • 本地宝 - 维权指南
```

---

## 🔧 常见问题

### Q1: 提示 "command not found: python3"

**解决**: 安装 Python 3.10+
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Windows
从 python.org 下载安装
```

### Q2: 提示 "command not found: legal-rights"

**原因**: 未安装命令或未添加到 PATH

**解决**: 使用模块方式运行
```bash
python3 -m legal_rights ask "问题"
```

或安装命令:
```bash
pip3 install -e .
```

### Q3: 提示 "未配置 API密钥"

**解决**: 检查 .env 文件
```bash
# 查看 .env 文件
cat .env

# 确认格式正确
DASHSCOPE_API_KEY=sk-xxxxx  # 不要有空格
```

### Q4: 抓取网页失败

**可能原因**:
1. 网络连接问题
2. 网站反爬虫

**解决**:
```bash
# 使用代理（如需要）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 重试构建
legal-rights build-kb --force
```

### Q5: 如何切换模型？

在 `.env` 文件中设置:
```env
# 手动指定模型
LLM_MODE=qwen  # claude, qwen, zhipu

# 或使用自动选择
LLM_MODE=auto
```

---

## 📚 更多资源

### 文档

- [README.md](README.md) - 项目完整介绍
- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - 详细配置指南
- [docs/FAQ.md](docs/FAQ.md) - 常见问题解答
- [docs/DOMESTIC_LLM_GUIDE.md](docs/DOMESTIC_LLM_GUIDE.md) - 国内大模型指南

### 命令帮助

```bash
# 查看所有命令
legal-rights --help

# 查看配置状态
legal-rights config

# 测试 API 连接
legal-rights test
```

### 获取帮助

- 📖 [常见问题](docs/FAQ.md)
- 🐛 [报告问题](https://github.com/YOUR_GITHUB_USERNAME/legal_rights/issues)
- 💬 [讨论区](https://github.com/YOUR_GITHUB_USERNAME/legal_rights/discussions)

---

## 🎯 下一步

1. ✅ 完成安装和配置
2. ✅ 构建知识库
3. 📝 尝试提问
4. 🚀 探索更多功能

**开始你的第一个问题吧！** 🎉

```bash
legal-rights ask "劳动合同法关于经济补偿的规定是什么？"
```

---

**祝使用愉快！如有问题，请查看 [FAQ](docs/FAQ.md)** 📖
