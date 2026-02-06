# 向量索引使用指南

本文档说明如何构建和使用向量索引进行语义检索。

## 📋 前置要求

### 1. API 密钥

向量索引需要 OpenAI API 密钥用于生成文本向量（Embedding）。

**获取 API 密钥**:
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 Secret Key
5. 复制并保存密钥

**配置密钥**:

在项目根目录的 `.env` 文件中添加：

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. 安装依赖

```bash
pip install openai faiss-cpu numpy
```

## 🏗️ 构建索引

### 完整流程

```python
from legal_rights.scraper import HTMLCleaner, ContentParser
from legal_rights.knowledge import VectorIndexer

# 1. 解析HTML内容
cleaner = HTMLCleaner()
parser = ContentParser()

html = open("sample.html").read()
cleaned_html, _ = cleaner.clean_and_extract(html)
structured = parser.parse(cleaned_html, url="https://example.com", title="标题")

# 2. 构建向量索引
indexer = VectorIndexer()
indexer.build_index([structured], show_progress=True)

# 3. 保存索引
indexer.save_index()
```

### 使用测试脚本

```bash
python -m legal_rights.scripts.test_vector_index
```

这将执行完整的测试流程：
1. 测试 Embedding 客户端
2. 测试文档分块
3. 构建向量索引
4. 测试知识检索

## 🔍 检索文档

### 基础检索

```python
from legal_rights.knowledge import KnowledgeRetriever

# 初始化检索器（自动加载索引）
retriever = KnowledgeRetriever(auto_load=True)

# 检索相关文档
query = "如何计算N+1经济补偿金？"
results = retriever.retrieve(query, top_k=5)

for doc, score in results:
    print(f"相似度: {score:.4f}")
    print(f"章节: {doc.section_title}")
    print(f"内容: {doc.content}")
```

### 高级检索

#### 1. 设置相似度阈值

```python
# 只返回相似度 > 0.5 的结果
results = retriever.retrieve(
    query="经济补偿",
    top_k=10,
    min_score=0.5
)
```

#### 2. 过滤特定章节

```python
# 只检索特定章节
results = retriever.retrieve(
    query="补偿标准",
    filter_section="经济补偿的计算方法"
)
```

#### 3. 获取上下文文本

```python
# 直接获取组合好的上下文
context = retriever.retrieve_with_context(
    query="维权流程",
    top_k=3
)
print(context)
```

#### 4. 关键词检索

```python
# 基于关键词匹配
keywords = ["N+1", "补偿金", "代通知金"]
results = retriever.retrieve_by_keyword(keywords, top_k=5)
```

#### 5. 混合检索

```python
# 结合向量相似度和关键词匹配
results = retriever.hybrid_retrieve(
    query="经济补偿计算",
    keywords=["补偿", "工资", "年限"],
    top_k=5,
    vector_weight=0.7  # 向量权重70%，关键词权重30%
)
```

## 📊 索引统计

### 查看索引信息

```python
retriever = KnowledgeRetriever(auto_load=True)
stats = retriever.get_stats()

print(f"已索引: {stats['indexed']}")
print(f"文档数: {stats['total_documents']}")
print(f"向量维度: {stats['vector_dimension']}")
print(f"来源: {stats['sources']}")
print(f"章节: {stats['sections']}")
```

### 查看统计文件

索引构建后会生成统计文件：

```bash
cat data/vectors/stats.json
```

输出示例：

```json
{
  "total_documents": 45,
  "vector_dimension": 1536,
  "index_type": "IndexFlatL2",
  "sources": [
    "https://example.com/sample"
  ],
  "sections": [
    "标题",
    "一、经济补偿的法律依据",
    "1.1 应支付经济补偿的情形",
    ...
  ]
}
```

## ⚙️ 配置参数

### 分块参数

在 `config.py` 或 `.env` 中配置：

```python
CHUNK_SIZE = 512      # 分块大小（字符数）
CHUNK_OVERLAP = 50    # 重叠大小（字符数）
```

较大的 `CHUNK_SIZE` 提供更多上下文，但可能降低检索精度。
较大的 `CHUNK_OVERLAP` 提高连续性，但增加存储开销。

### 检索参数

```python
TOP_K_RESULTS = 5     # 默认返回的结果数量
```

### Embedding 模型

默认使用 `text-embedding-3-small`（1536维）。

如需更高精度，可在 `config.py` 中修改：

```python
EMBEDDING_MODEL = "text-embedding-3-large"  # 3072维，成本更高
```

## 💰 成本估算

### OpenAI Embedding API 定价

| 模型 | 价格 | 维度 |
|------|------|------|
| text-embedding-3-small | $0.02 / 1M tokens | 1536 |
| text-embedding-3-large | $0.13 / 1M tokens | 3072 |

### 示例成本

假设知识库有 **50,000 字符**（约 12,500 tokens）：

- **构建索引**: $0.02 × (12,500 / 1,000,000) = **$0.00025**
- **单次查询**: $0.02 × (50 / 1,000,000) = **$0.000001**

**结论**: 成本极低，可忽略不计。

## 📁 文件结构

索引构建后会生成以下文件：

```
data/vectors/
├── index.faiss        # FAISS 向量索引（二进制）
├── metadata.pkl       # 文档元数据（Python pickle）
└── stats.json         # 统计信息（JSON）
```

## 🔧 故障排除

### 问题1: "Index not found"

**原因**: 索引文件不存在

**解决**:
```bash
python scripts/test_vector_index.py
```

### 问题2: "OpenAI API key is required"

**原因**: API 密钥未配置

**解决**:
1. 检查 `.env` 文件是否存在
2. 确认 `OPENAI_API_KEY` 正确配置
3. 重启 Python 进程

### 问题3: Rate limit exceeded

**原因**: 请求频率过高

**解决**:

在 `.env` 中降低速率限制：

```env
RATE_LIMIT_PER_SECOND=2
```

### 问题4: 检索结果不相关

**可能原因**:
1. 查询表达不够准确
2. 分块参数不合适
3. 知识库内容不足

**解决**:
1. 尝试不同的查询方式
2. 调整 `CHUNK_SIZE` 和 `CHUNK_OVERLAP`
3. 使用混合检索（结合关键词）
4. 扩充知识库内容

## 🚀 最佳实践

### 1. 定期更新索引

法律法规可能更新，建议定期重建索引：

```bash
# 删除旧索引
rm -rf data/vectors/*

# 重新构建
python scripts/test_vector_index.py
```

### 2. 调优检索参数

根据实际效果调整：

- **top_k**: 返回更多结果提高召回率，但可能引入噪声
- **min_score**: 设置阈值过滤低相关性结果
- **vector_weight**: 平衡向量和关键词的权重

### 3. 监控成本

虽然成本很低，但仍建议监控 OpenAI API 使用：

```bash
# 查看 API 使用情况
# https://platform.openai.com/usage
```

### 4. 备份索引

索引文件很小，建议备份：

```bash
tar -czf vectors_backup_$(date +%Y%m%d).tar.gz data/vectors/
```

## 📚 参考资料

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [向量检索最佳实践](https://www.pinecone.io/learn/vector-search/)

---

**版本**: 1.0
**更新日期**: 2026-02-06
