# 📦 上传到 GitHub 的命令

## 快速上传（推荐）

执行我为你准备的脚本：

```bash
cd /Users/nat.mei/data/Claude-Project/legal_rights
./upload_to_github.sh
```

脚本会自动完成所有步骤。

---

## 手动上传（逐步执行）

如果你想手动执行，按照以下步骤：

### 步骤 1: 初始化 Git

```bash
cd /Users/nat.mei/data/Claude-Project/legal_rights
git init
```

### 步骤 2: 添加所有文件

```bash
git add .
```

### 步骤 3: 创建提交

```bash
git commit -m "Initial commit: Legal Rights AI Assistant v1.0.2

- 完整的 RAG 架构实现
- 支持 Claude 4.5 和国内大模型（通义千问、智谱AI）
- FAISS 向量检索
- 完整的文档体系（11个专题文档）
- MIT 开源协议

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

### 步骤 4: 添加远程仓库

```bash
git remote add origin https://github.com/natmusissunny/legal_rights.git
```

### 步骤 5: 重命名分支为 main

```bash
git branch -M main
```

### 步骤 6: 推送到 GitHub

**如果是新仓库（推荐）：**

```bash
git push -u origin main
```

**如果仓库已有内容需要覆盖：**

```bash
git push -u origin main --force
```

---

## ✅ 完成后验证

1. 访问你的仓库：
   https://github.com/natmusissunny/legal_rights

2. 检查文件是否都上传成功

3. 查看 README.md 是否正确显示

---

## 📋 发布后的配置

### 1. 添加仓库描述

在仓库主页点击 "About" 旁的设置图标，添加：

**Description:**
```
法律维权智能助手 | AI-powered legal rights assistant for labor law consultation based on RAG architecture
```

**Website:**
```
https://github.com/natmusissunny/legal_rights
```

**Topics (标签):**
```
python
rag
ai
legal-tech
nlp
llm
claude
vector-database
chinese
labor-law
legal-assistant
chatbot
knowledge-base
faiss
anthropic
```

### 2. 创建 Release

访问：https://github.com/natmusissunny/legal_rights/releases/new

或使用命令（如果安装了 gh CLI）：

```bash
gh release create v1.0.2 \
  --title "v1.0.2 - Initial Release" \
  --notes "首次发布

## 功能特性

- 🚀 完整的 RAG 架构实现
- 🇨🇳 支持国内大模型（通义千问、智谱AI）
- 📊 FAISS 向量检索
- 🤖 Claude 4.5 / 通义千问
- 📚 完整的知识库构建
- 💬 多轮对话支持
- 📊 答案溯源可追踪

## 文档

- 11 个专题文档
- 23 个常见问题解答
- 完整的快速开始指南

## 技术栈

Python 3.10+ | Claude 4.5 | FAISS | OpenAI Embedding

成本低至 ¥0.0075/次查询（国内大模型方案）"
```

### 3. 配置仓库设置（可选）

**Settings → General:**
- ✅ Issues
- ✅ Discussions
- ❌ Wikis（我们用 docs/）
- ❌ Projects

**Settings → Pages（可选）:**
如果想托管文档：
- Source: Deploy from a branch
- Branch: main
- Folder: /docs

---

## 🔧 常见问题

### Q1: 推送时要求输入密码

**原因**: GitHub 不再支持密码认证

**解决方案**:

方案A - 使用 Personal Access Token:
1. 访问 https://github.com/settings/tokens
2. 生成新 token（repo 权限）
3. 推送时使用 token 作为密码

方案B - 使用 SSH（推荐）:
```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 添加到 GitHub
# 复制公钥：cat ~/.ssh/id_ed25519.pub
# 访问 https://github.com/settings/keys 添加

# 3. 修改远程仓库 URL
git remote set-url origin git@github.com:natmusissunny/legal_rights.git

# 4. 推送
git push -u origin main
```

### Q2: 推送失败 "Updates were rejected"

**原因**: 远程仓库有内容，本地仓库没有

**解决方案**:

```bash
# 拉取远程内容（如果需要保留）
git pull origin main --allow-unrelated-histories

# 或直接强制推送（覆盖远程）
git push -u origin main --force
```

### Q3: 部分文件没有上传

**检查**: 确认 .gitignore 没有忽略重要文件

```bash
# 查看被忽略的文件
git status --ignored

# 强制添加某个被忽略的文件
git add -f path/to/file
```

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 Git 状态：`git status`
2. 查看远程仓库：`git remote -v`
3. 查看提交历史：`git log --oneline`

---

**准备好了吗？开始上传吧！** 🚀
