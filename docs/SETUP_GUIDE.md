# 配置指南

本文档提供法律维权智能助手的详细配置步骤。

## 📋 前置要求

### 系统要求

- **操作系统**: macOS / Linux / Windows
- **Python 版本**: 3.10 或更高
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 500MB 用于依赖和知识库

### 必需的 API 密钥

本项目需要两个 API 密钥：

1. **Claude API 密钥** - 用于大语言模型问答
2. **OpenAI API 密钥** - 用于文本向量化 (Embedding)

## 🔑 获取 API 密钥

### 1. 获取 Claude API 密钥

#### 步骤 1: 注册账号

访问 [Anthropic Console](https://console.anthropic.com/)，注册或登录账号。

#### 步骤 2: 创建 API 密钥

1. 登录后，点击右上角的 "API Keys"
2. 点击 "Create Key" 按钮
3. 为密钥命名（例如：legal_rights_project）
4. 点击 "Create"
5. **重要**: 立即复制并保存密钥（只显示一次）

#### 步骤 3: 充值（如需要）

- Claude API 采用按量付费模式
- 建议充值 $5-10 开始测试
- 查看定价: https://www.anthropic.com/pricing

**密钥格式**:
```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. 获取 OpenAI API 密钥

#### 步骤 1: 注册账号

访问 [OpenAI Platform](https://platform.openai.com/)，注册或登录账号。

#### 步骤 2: 创建 API 密钥

1. 登录后，点击右上角头像 → "View API keys"
2. 点击 "Create new secret key" 按钮
3. 为密钥命名（例如：legal_rights_embedding）
4. 点击 "Create secret key"
5. **重要**: 立即复制并保存密钥（只显示一次）

#### 步骤 3: 充值（如需要）

- OpenAI API 采用按量付费模式
- Embedding API 成本极低（$0.02/1M tokens）
- 建议充值 $5 即可使用很久
- 查看定价: https://openai.com/pricing

**密钥格式**:
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## ⚙️ 配置环境变量

### 方法 1: 使用 .env 文件（推荐）

#### 步骤 1: 复制模板

在项目根目录下执行：

```bash
cd .
cp .env.example .env
```

#### 步骤 2: 编辑 .env 文件

使用任意文本编辑器打开 `.env` 文件：

```bash
# macOS/Linux
nano .env
# 或
vim .env
# 或
code .env  # VS Code

# Windows
notepad .env
```

#### 步骤 3: 填入 API 密钥

将您的实际密钥替换到以下位置：

```env
# Claude API密钥（必需）
CLAUDE_API_KEY=sk-ant-api03-your-actual-claude-key-here

# OpenAI API密钥（必需，用于Embedding）
OPENAI_API_KEY=sk-your-actual-openai-key-here

# 可选配置

# 速率限制（每秒请求数，默认4）
RATE_LIMIT_PER_SECOND=4

# 文档分块大小（tokens，默认512）
# CHUNK_SIZE=512

# 分块重叠大小（tokens，默认50）
# CHUNK_OVERLAP=50

# 检索返回Top-K结果（默认5）
# TOP_K_RESULTS=5
```

#### 步骤 4: 保存文件

保存并关闭编辑器。

**安全提示**:
- ✅ `.env` 文件已在 `.gitignore` 中，不会被提交到 Git
- ❌ 不要将 `.env` 文件发送给他人或上传到公开位置
- ❌ 不要在代码中硬编码 API 密钥

### 方法 2: 使用环境变量

如果您不想创建 `.env` 文件，可以直接设置环境变量：

#### macOS / Linux

```bash
# 临时设置（仅当前终端会话有效）
export CLAUDE_API_KEY="sk-ant-api03-your-key"
export OPENAI_API_KEY="sk-your-key"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export CLAUDE_API_KEY="sk-ant-api03-your-key"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)

```powershell
# 临时设置
$env:CLAUDE_API_KEY="sk-ant-api03-your-key"
$env:OPENAI_API_KEY="sk-your-key"

# 永久设置
[System.Environment]::SetEnvironmentVariable('CLAUDE_API_KEY', 'sk-ant-api03-your-key', 'User')
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key', 'User')
```

## 📦 安装依赖

### 使用 pip 安装

在项目根目录下执行：

```bash
cd .
pip install -r requirements.txt
```

### 使用虚拟环境（推荐）

为了避免依赖冲突，建议使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 验证安装

```bash
pip list | grep -E "httpx|pydantic|beautifulsoup4|reportlab|faiss|anthropic|openai"
```

应该看到类似输出：

```
anthropic        0.25.0
beautifulsoup4   4.12.0
faiss-cpu        1.8.0
httpx            0.27.0
openai           1.0.0
pydantic         2.6.0
reportlab        4.0.0
...
```

## ✅ 验证配置

### 测试 API 连接

运行测试命令：

```bash
python -m legal_rights test
```

**成功输出示例**:

```
🔍 测试API连接...
============================================================

🔑 API密钥状态:
==================================================
✅ Claude API: sk-ant-api03...abc
   来源: .env 文件
✅ OpenAI API: sk-...xyz
   来源: .env 文件
==================================================

🚧 完整的API测试功能开发中...
```

**失败输出示例**:

```
❌ 配置验证失败！

请按照以下步骤配置API密钥：
1. 复制 .env.example 为 .env
2. 在 .env 文件中填入您的 CLAUDE_API_KEY 和 OPENAI_API_KEY
```

### 检查数据目录

运行统计命令：

```bash
python -m legal_rights stats
```

应该看到数据目录已创建：

```
📊 知识库统计信息
============================================================

📁 数据目录:
  - 缓存目录: ./data/cache
    文件数: 0
  - PDF目录: ./data/knowledge
    PDF数: 0
  - 向量目录: ./data/vectors
    文件数: 0

⚠️  知识库尚未构建
请先运行: python -m legal_rights build-kb
```

## 🚀 下一步

配置完成后，您可以：

1. **构建知识库**:
   ```bash
   python -m legal_rights build-kb
   ```

2. **开始问答**:
   ```bash
   python -m legal_rights ask "公司恶意辞退不给补偿怎么办？"
   ```

3. **交互式对话**:
   ```bash
   python -m legal_rights chat
   ```

## 🔧 高级配置

### 调整向量检索参数

在 `.env` 文件中添加：

```env
# 文档分块大小（建议范围: 256-1024）
CHUNK_SIZE=512

# 分块重叠大小（建议范围: 20-100）
CHUNK_OVERLAP=50

# 检索返回Top-K结果（建议范围: 3-10）
TOP_K_RESULTS=5
```

**参数说明**:
- `CHUNK_SIZE`: 越大则上下文越完整，但检索精度可能降低
- `CHUNK_OVERLAP`: 越大则相邻块的连贯性越好，但存储开销增加
- `TOP_K_RESULTS`: 越大则召回更多相关文档，但可能引入噪声

### 调整速率限制

如果您的 API 计划支持更高的 QPS（每秒查询数）：

```env
# 默认 4 次/秒
RATE_LIMIT_PER_SECOND=10
```

### 切换 Embedding 模型

默认使用 `text-embedding-3-small`，您可以在 `config.py` 中修改：

```python
# 可选模型:
# - text-embedding-3-small (默认，性价比高)
# - text-embedding-3-large (精度更高，成本更高)
# - text-embedding-ada-002 (旧版模型)
EMBEDDING_MODEL: str = "text-embedding-3-large"
```

### 切换 Claude 模型

默认使用 `claude-3-5-sonnet-20240620`，您可以在 `config.py` 中修改：

```python
# 可选模型:
# - claude-3-5-sonnet-20240620 (默认，平衡性能和成本)
# - claude-3-opus-20240229 (最高质量，成本最高)
# - claude-3-haiku-20240307 (最快速度，成本最低)
CLAUDE_MODEL: str = "claude-3-opus-20240229"
```

## ❓ 常见问题

### Q1: 提示 "Module not found"

**原因**: 依赖未正确安装

**解决**:
```bash
pip install -r requirements.txt --force-reinstall
```

### Q2: Claude API 返回 401 错误

**原因**: API 密钥无效或过期

**解决**:
1. 检查密钥是否正确复制（没有多余空格）
2. 在 Anthropic Console 验证密钥是否有效
3. 检查账户余额是否充足

### Q3: OpenAI API 返回 429 错误

**原因**: 达到速率限制或余额不足

**解决**:
1. 降低 `RATE_LIMIT_PER_SECOND`
2. 检查账户余额
3. 等待一段时间后重试

### Q4: 如何更新 API 密钥？

直接编辑 `.env` 文件，保存后重新运行命令即可（无需重启）。

### Q5: 知识库构建失败

**可能原因**:
- 网络连接问题
- 目标网站结构变化
- 磁盘空间不足

**解决**:
1. 检查网络连接
2. 使用 `--force` 强制重建: `python -m legal_rights build-kb --force`
3. 查看错误日志

## 📞 获取帮助

如果遇到其他问题：

1. 查看 [README.md](../README.md) 了解项目概况
2. 查看 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解架构设计
3. 查看 [API_GUIDE.md](./API_GUIDE.md) 了解 API 使用

---

**文档版本**: 1.0
**更新日期**: 2026-02-06
