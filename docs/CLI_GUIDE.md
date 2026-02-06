# CLI 使用指南

本文档说明如何使用法律维权智能助手的命令行工具。

## 🚀 快速开始

### 基本语法

```bash
python -m legal_rights <command> [options]
```

### 获取帮助

```bash
# 查看所有命令
python -m legal_rights --help

# 查看特定命令的帮助
python -m legal_rights ask --help
python -m legal_rights build-kb --help
```

## 📚 命令列表

### 1. build-kb - 构建知识库

从网页抓取法律内容并构建向量索引。

**语法**:
```bash
python -m legal_rights build-kb [--force] [--skip-scrape]
```

**选项**:
- `--force`: 强制重新抓取网页（忽略缓存）
- `--skip-scrape`: 跳过网页抓取，使用现有缓存

**示例**:
```bash
# 首次构建（完整流程）
python -m legal_rights build-kb

# 强制重新构建
python -m legal_rights build-kb --force

# 只重建索引（跳过抓取）
python -m legal_rights build-kb --skip-scrape
```

**流程**:
1. 抓取目标网页（或使用缓存）
2. 清洗和解析HTML
3. 生成Markdown文档
4. 构建FAISS向量索引

**输出**:
- `data/cache/` - 缓存的HTML
- `data/knowledge/` - Markdown文档
- `data/vectors/` - 向量索引

### 2. ask - 单次问答

向AI提问并获得答案。

**语法**:
```bash
python -m legal_rights ask "问题" [--verbose] [--top-k N]
```

**选项**:
- `--verbose`: 显示详细信息（包括检索的文档片段）
- `--top-k N`: 检索N个文档（默认5）

**示例**:
```bash
# 基础问答
python -m legal_rights ask "如何计算N+1补偿？"

# 详细模式
python -m legal_rights ask "被辞退有补偿吗？" --verbose

# 检索更多文档
python -m legal_rights ask "维权流程" --top-k 10
```

**示例问题**:
- "公司恶意辞退不给补偿怎么办？"
- "工作3年月薪8000元，N+1补偿是多少？"
- "劳动仲裁需要什么材料？"
- "经济补偿的法律依据是什么？"

### 3. chat - 交互式对话

启动交互式对话模式，支持多轮对话。

**语法**:
```bash
python -m legal_rights chat [--reset]
```

**选项**:
- `--reset`: 清空对话历史

**交互命令**:
- 输入问题并按回车 - 提问
- `quit` 或 `exit` - 退出
- `reset` - 重置对话历史
- `summary` - 查看对话摘要

**示例会话**:
```bash
python -m legal_rights chat

[0] 您: 我在公司工作了3年
[1] 助手: 我了解了...

[1] 您: 被公司辞退了
[2] 助手: 根据劳动法...

[2] 您: 应该赔多少？
[3] 助手: 根据您提供的信息...

[3] 您: summary
📊 对话摘要:
...

[3] 您: quit
👋 再见！
```

### 4. test - 测试API连接

测试Claude和OpenAI API是否正常工作。

**语法**:
```bash
python -m legal_rights test
```

**测试内容**:
1. API密钥状态
2. Claude API连接
3. OpenAI Embedding API连接

**示例输出**:
```
🔍 测试API连接
============================================================

[1] API密钥状态
--------------------------------------------------------------
✅ Claude API: sk-ant-api03...abc
   来源: .env 文件
✅ OpenAI API: sk-...xyz
   来源: .env 文件

[2] 测试 Claude API
--------------------------------------------------------------
正在调用Claude API... ✅ 成功
响应: 经济补偿金是指用人单位解除劳动合同时...

[3] 测试 OpenAI Embedding API
--------------------------------------------------------------
正在生成向量... ✅ 成功
向量维度: 1536
向量前5维: [0.123, -0.456, ...]
```

### 5. stats - 显示统计信息

查看知识库的构建状态和统计信息。

**语法**:
```bash
python -m legal_rights stats
```

**显示信息**:
- 缓存文件数量
- 生成的文档数量
- 向量索引统计
- 知识库状态

**示例输出**:
```
📊 知识库统计信息
============================================================

📁 数据目录:
  - 缓存目录: .../data/cache
    HTML文件: 3
  - 文档目录: .../data/knowledge
    Markdown: 3
    文本文件: 3
  - 向量目录: .../data/vectors
    文件数: 3

📈 向量索引统计:
  - 文档数: 45
  - 向量维度: 1536
  - 索引类型: IndexFlatL2
  - 数据源数: 3
  - 章节数: 22

🎯 知识库状态:
  ✅ 知识库完整
     可以使用: python -m legal_rights ask "问题"
```

## 🔧 使用场景

### 场景1: 首次使用

```bash
# 1. 配置API密钥
cp .env.example .env
nano .env  # 填入API密钥

# 2. 构建知识库
python -m legal_rights build-kb

# 3. 测试
python -m legal_rights test

# 4. 开始使用
python -m legal_rights ask "如何计算补偿金？"
```

### 场景2: 网页抓取失败

如果网页抓取失败（反爬虫）：

```bash
# 1. 手动下载HTML到 data/cache/
# 参考: scripts/manual_scrape_guide.md

# 2. 跳过抓取，直接构建
python -m legal_rights build-kb --skip-scrape
```

### 场景3: 更新知识库

```bash
# 强制重新抓取和构建
python -m legal_rights build-kb --force
```

### 场景4: 只重建索引

```bash
# 内容已有，只需重建索引
python -m legal_rights build-kb --skip-scrape
```

### 场景5: 交互式咨询

```bash
# 启动交互模式
python -m legal_rights chat

# 多轮对话
您: 我工作了5年
助手: ...
您: 月薪12000元
助手: ...
您: 被辞退应该赔多少？
助手: ...
```

## ⚙️ 配置

### 环境变量

在 `.env` 文件中配置：

```env
# 必需
CLAUDE_API_KEY=sk-ant-api03-your-key
OPENAI_API_KEY=sk-your-key

# 可选
RATE_LIMIT_PER_SECOND=4
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

### 工作目录

CLI需要在项目根目录运行：

```bash
cd /path/to/legal_rights
python -m legal_rights <command>
```

### 数据目录

所有数据存储在 `data/` 目录：

```
data/
├── cache/           # HTML缓存
├── knowledge/       # 生成的文档
└── vectors/         # 向量索引
```

## 🔍 故障排除

### 问题1: "No module named legal_rights"

**原因**: 不在项目目录下

**解决**:
```bash
cd /path/to/workspace
python -m legal_rights --help
```

### 问题2: "配置验证失败"

**原因**: API密钥未配置

**解决**:
```bash
# 创建 .env 文件
cp .env.example .env

# 编辑并添加密钥
nano .env
```

### 问题3: "向量索引不存在"

**原因**: 知识库未构建

**解决**:
```bash
python -m legal_rights build-kb
```

### 问题4: 网页抓取失败

**原因**: 网站反爬虫

**解决**:
```bash
# 方案1: 手动下载HTML
# 参考: scripts/manual_scrape_guide.md

# 方案2: 使用示例HTML
cp data/cache/sample_legal_content.html data/cache/

# 方案3: 跳过抓取
python -m legal_rights build-kb --skip-scrape
```

### 问题5: API调用失败

**可能原因**:
- 网络问题
- API密钥无效
- 余额不足
- 速率限制

**解决**:
```bash
# 测试API
python -m legal_rights test

# 检查错误信息
# 验证API密钥
# 检查账户余额
```

## 💡 使用技巧

### 1. 善用详细模式

查看检索到的原文：
```bash
python -m legal_rights ask "问题" --verbose
```

### 2. 调整检索数量

检索更多相关文档：
```bash
python -m legal_rights ask "问题" --top-k 10
```

### 3. 利用对话上下文

```bash
python -m legal_rights chat
您: 我工作了3年
您: 月薪8000
您: 被辞退应该赔多少？
# AI会综合之前的信息回答
```

### 4. 定期更新知识库

```bash
# 每月更新一次
python -m legal_rights build-kb --force
```

### 5. 检查知识库状态

```bash
# 确认一切正常
python -m legal_rights stats
```

## 📊 性能说明

### 命令响应时间

| 命令 | 响应时间 | 说明 |
|------|---------|------|
| build-kb | 3-5分钟 | 首次构建，包含API调用 |
| ask | 3-8秒 | 检索 + Claude生成 |
| chat | 3-8秒/轮 | 同ask |
| test | 5-10秒 | API测试 |
| stats | <1秒 | 本地统计 |

### 成本估算

- build-kb: < $0.01（一次性）
- ask: ~$0.013/次
- chat: ~$0.013/轮

## 🔗 相关文档

- [项目README](../README.md)
- [配置指南](SETUP_GUIDE.md)
- [Agent使用指南](AGENT_GUIDE.md)
- [向量索引指南](VECTOR_INDEX_GUIDE.md)

## 📝 常见用例

### 计算补偿金

```bash
python -m legal_rights ask "工作3年月薪8000元，被辞退应该赔多少？"
```

### 查询维权流程

```bash
python -m legal_rights ask "公司不给补偿怎么办？"
```

### 查询法律依据

```bash
python -m legal_rights ask "N+1补偿的法律依据是什么？"
```

### 交互式咨询

```bash
python -m legal_rights chat
您: 我的情况比较复杂
助手: 请详细说明...
您: 我工作了5年，月薪12000
助手: 了解了...
您: 公司说要裁员
助手: ...
```

---

**版本**: 1.0
**更新日期**: 2026-02-06
