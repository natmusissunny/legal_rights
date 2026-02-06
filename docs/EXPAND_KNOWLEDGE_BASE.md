# 知识库扩展指南

本文档说明如何添加新的法律文档到RAG检索系统中。

## 📊 当前知识库状态

根据现有数据：

```json
{
  "total_documents": 37,           // 37个文档块
  "vector_dimension": 1536,        // 1536维向量
  "sources": 3,                    // 3个数据源
  "sections": 29                   // 29个章节
}
```

**现有数据源**:
1. ✅ `m12333.cn` - 人社部12333平台
2. ✅ `hshfy.sh.cn` - 上海市高级人民法院
3. ✅ `bendibao.com` - 上海本地宝

**覆盖范围**:
- ✅ 经济补偿计算
- ✅ 维权流程
- ✅ 劳动法基础
- ⚠️ **数据量较少**（仅37个文档块）

## 🎯 数据全面性评估

### 当前限制

1. **数据源少** (仅3个网站)
2. **内容深度不足** (每个网站只抓取了1个页面)
3. **覆盖面窄** (主要是上海地区政策)
4. **案例缺乏** (没有实际判例)

### 建议补充的内容

| 类型 | 推荐来源 | 优先级 |
|-----|---------|--------|
| **官方法规** | 全国人大、国务院 | 🔴 高 |
| **司法解释** | 最高法、最高检 | 🔴 高 |
| **判例文书** | 中国裁判文书网 | 🟡 中 |
| **地方政策** | 各地人社局 | 🟢 低 |
| **专业解读** | 律师事务所、法律网站 | 🟢 低 |

## 🚀 添加新数据源的方法

### 方法1: 添加网页URL（推荐）

#### 步骤1: 编辑配置文件

```bash
cd .
nano config.py
```

在`TARGET_URLS`列表中添加新URL：

```python
# 目标URL列表
TARGET_URLS = [
    # 现有URL
    "https://m12333.cn/qa/myyuf.html",
    "https://www.hshfy.sh.cn/shfy/web/xxnr.jsp?pa=aaWQ9MjAxNzcwODUmeGg9MSZsbWRtPWxtNTE5z&zd=xwzx",
    "https://sh.bendibao.com/zffw/2022831/258695.shtm",

    # 新增URL ✨
    "http://www.npc.gov.cn/npc/c30834/202101/bfe9b0eb39c04124a4a52e1a2ef11eb8.shtml",  # 劳动合同法全文
    "https://www.court.gov.cn/fabu-xiangqing-123456.html",  # 最高法司法解释
    "https://www.12333.gov.cn/example.html",  # 更多案例
]
```

#### 步骤2: 重新构建知识库

```bash
python -m legal_rights build-kb --force
```

**参数说明**:
- `--force`: 强制重新抓取（忽略缓存）
- 不加`--force`: 只抓取新URL，保留已有缓存

#### 步骤3: 验证

```bash
# 查看新的统计信息
python -m legal_rights stats

# 测试问答
python -m legal_rights ask "劳动合同法第三十九条规定了什么？"
```

### 方法2: 手动添加本地文件

如果您有PDF、Word、TXT等文件：

#### 步骤1: 转换为Markdown

```bash
# 创建新文档
nano data/knowledge/我的法律文档.md
```

**格式要求**:
```markdown
# 文档标题

来源: https://example.com/source

## 第一章 标题

正文内容...

## 第二章 标题

正文内容...
```

#### 步骤2: 手动向量化并添加到索引

创建Python脚本 `add_local_file.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legal_rights.models import StructuredContent, LegalSection
from legal_rights.knowledge import VectorIndexer

# 读取您的文档
file_path = "data/knowledge/我的法律文档.md"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 创建结构化内容
structured = StructuredContent(
    url="file://" + file_path,
    title="我的法律文档",
    scraped_at="2026-02-06",
    sections=[
        LegalSection(
            title="完整内容",
            content=content,
            level=1
        )
    ]
)

# 加载现有索引
indexer = VectorIndexer()
indexer.load_index()

# 添加新文档
print("正在向量化新文档...")
indexer.add_documents([structured], show_progress=True)

# 保存索引
indexer.save_index()
print("✅ 已添加到知识库")
```

运行脚本：
```bash
python add_local_file.py
```

### 方法3: 批量导入（高级）

如果您有大量文档（如100+个PDF）：

#### 步骤1: 准备文档目录

```bash
mkdir -p data/import/
# 将所有PDF/DOC/TXT文件放入这个目录
```

#### 步骤2: 创建批量导入脚本

```python
# scripts/batch_import.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legal_rights.knowledge import VectorIndexer
from legal_rights.models import StructuredContent, LegalSection

def import_directory(dir_path: Path):
    """批量导入目录中的所有文件"""
    indexer = VectorIndexer()
    indexer.load_index()

    # 支持的文件格式
    patterns = ['*.txt', '*.md', '*.pdf', '*.docx']

    documents = []
    for pattern in patterns:
        for file_path in dir_path.glob(pattern):
            print(f"处理: {file_path.name}")

            # 读取文件内容
            if file_path.suffix == '.txt' or file_path.suffix == '.md':
                content = file_path.read_text(encoding='utf-8')
            elif file_path.suffix == '.pdf':
                # 需要安装: pip install PyPDF2
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    content = '\n'.join(page.extract_text() for page in pdf.pages)
            elif file_path.suffix == '.docx':
                # 需要安装: pip install python-docx
                import docx
                doc = docx.Document(file_path)
                content = '\n'.join(para.text for para in doc.paragraphs)
            else:
                continue

            # 创建结构化内容
            structured = StructuredContent(
                url=f"file://{file_path}",
                title=file_path.stem,
                scraped_at="2026-02-06",
                sections=[
                    LegalSection(title="正文", content=content, level=1)
                ]
            )
            documents.append(structured)

    # 批量添加
    print(f"\n开始向量化 {len(documents)} 个文档...")
    indexer.add_documents(documents, show_progress=True)
    indexer.save_index()
    print(f"✅ 成功导入 {len(documents)} 个文档")

if __name__ == "__main__":
    import_dir = Path("data/import/")
    import_directory(import_dir)
```

运行：
```bash
python scripts/batch_import.py
```

## 📚 推荐的数据源

### 官方权威来源

#### 1. 法律法规全文

| 来源 | URL | 说明 |
|-----|-----|------|
| 劳动合同法 | http://www.npc.gov.cn/npc/c30834/202101/bfe9b0eb39c04124a4a52e1a2ef11eb8.shtml | 全国人大 |
| 劳动法 | http://www.npc.gov.cn/npc/c238/c10005.shtml | 全国人大 |
| 劳动争议调解仲裁法 | http://www.npc.gov.cn/npc/c238/c9999.shtml | 全国人大 |
| 社会保险法 | http://www.npc.gov.cn/npc/c238/c10006.shtml | 全国人大 |

#### 2. 司法解释

| 来源 | URL | 说明 |
|-----|-----|------|
| 最高法劳动争议司法解释（一） | https://www.court.gov.cn/... | 最高人民法院 |
| 最高法劳动争议司法解释（二） | https://www.court.gov.cn/... | 最高人民法院 |
| 最高法劳动争议司法解释（三） | https://www.court.gov.cn/... | 最高人民法院 |
| 最高法劳动争议司法解释（四） | https://www.court.gov.cn/... | 最高人民法院 |

#### 3. 判例文书（可选）

| 来源 | URL | 说明 |
|-----|-----|------|
| 中国裁判文书网 | https://wenshu.court.gov.cn/ | 需要搜索关键词 |
| 北大法宝 | https://www.pkulaw.com/ | 需要付费账号 |

#### 4. 地方政策

| 地区 | 来源 | URL |
|-----|-----|-----|
| 北京 | 北京市人社局 | http://rsj.beijing.gov.cn/ |
| 上海 | 上海市人社局 | http://rsj.sh.gov.cn/ |
| 广东 | 广东省人社厅 | http://hrss.gd.gov.cn/ |
| 深圳 | 深圳市人社局 | http://hrss.sz.gov.cn/ |

### 专业内容平台

| 平台 | URL | 优势 | 劣势 |
|-----|-----|------|------|
| 无讼 | https://www.itslaw.com/ | 案例丰富 | 需付费 |
| 法律快车 | https://www.lawtime.cn/ | 通俗易懂 | 质量参差 |
| 华律网 | https://www.66law.cn/ | 覆盖面广 | 广告较多 |
| 找法网 | https://www.findlaw.cn/ | 案例多 | 需筛选 |

## 🔧 高级扩展方法

### 1. 添加特定章节过滤

如果某个网页内容很多，只想要其中某些章节：

```python
# 在 scraper/content_parser.py 中
def parse(self, html: str, url: str, title: str) -> StructuredContent:
    # ... 解析逻辑 ...

    # 过滤特定章节
    filtered_sections = [
        section for section in sections
        if "经济补偿" in section.title or "劳动仲裁" in section.title
    ]

    return StructuredContent(
        url=url,
        title=title,
        sections=filtered_sections,  # 只保留相关章节
        scraped_at=datetime.now()
    )
```

### 2. 自定义文档权重

给不同来源的文档设置不同权重：

```python
# 在检索时应用权重
class WeightedRetriever:
    WEIGHTS = {
        "npc.gov.cn": 2.0,      # 官方法规，权重最高
        "court.gov.cn": 1.8,    # 司法解释
        "12333.cn": 1.5,        # 官方解读
        "default": 1.0          # 其他来源
    }

    def retrieve(self, query: str, top_k: int = 5):
        results = self.indexer.search(query, top_k=top_k * 2)

        # 应用权重
        weighted_results = []
        for doc, score in results:
            weight = self._get_weight(doc.source_url)
            weighted_score = score * weight
            weighted_results.append((doc, weighted_score))

        # 重新排序
        weighted_results.sort(key=lambda x: x[1], reverse=True)
        return weighted_results[:top_k]
```

### 3. 增量更新知识库

只添加新文档，不重建整个索引：

```python
# scripts/incremental_update.py
from legal_rights.knowledge import VectorIndexer
from legal_rights.models import StructuredContent, LegalSection

def incremental_update(new_documents: List[StructuredContent]):
    """增量更新知识库"""
    indexer = VectorIndexer()

    # 加载现有索引
    indexer.load_index()
    print(f"当前文档数: {len(indexer.documents)}")

    # 添加新文档
    indexer.add_documents(new_documents, show_progress=True)

    # 保存
    indexer.save_index()
    print(f"更新后文档数: {len(indexer.documents)}")
```

## 📊 数据质量优化

### 1. 文档去重

避免重复内容：

```python
def deduplicate_documents(documents: List[StructuredContent]):
    """去除重复文档"""
    seen_urls = set()
    unique_docs = []

    for doc in documents:
        if doc.url not in seen_urls:
            seen_urls.add(doc.url)
            unique_docs.append(doc)

    return unique_docs
```

### 2. 内容质量过滤

过滤低质量内容：

```python
def filter_quality(sections: List[LegalSection]) -> List[LegalSection]:
    """过滤低质量章节"""
    filtered = []
    for section in sections:
        # 过滤太短的章节（可能是导航、广告等）
        if len(section.content) < 50:
            continue

        # 过滤包含特定关键词的章节
        if any(kw in section.content for kw in ["广告", "推广", "联系我们"]):
            continue

        filtered.append(section)

    return filtered
```

### 3. 文档切分优化

优化文档块大小：

```python
# 在 config.py 中调整
CHUNK_SIZE: int = 512      # 增大到1024以保留更多上下文
CHUNK_OVERLAP: int = 50    # 增大到100以提高连贯性
TOP_K_RESULTS: int = 5     # 增大到10以检索更多文档
```

## 🧪 测试新数据源

添加新数据源后，务必测试：

### 1. 基础测试

```bash
# 查看统计信息
python -m legal_rights stats

# 期望: total_documents 增加
```

### 2. 检索测试

```bash
# 测试新内容是否可检索
python -m legal_rights ask "新数据源中的问题" --verbose

# 查看检索到的文档是否包含新来源
```

### 3. 质量测试

```bash
# 批量测试
python scripts/batch_test_questions.py

# 查看置信度是否提升
```

### 4. 覆盖率测试

创建测试问题集，确保新数据源覆盖的主题：

```python
# 新数据源相关问题
NEW_SOURCE_QUESTIONS = [
    "劳动合同法第三十九条规定了什么？",  # 如果添加了法律全文
    "最高法对加班费有什么司法解释？",    # 如果添加了司法解释
    "北京市的经济补偿标准是多少？",      # 如果添加了地方政策
]

for question in NEW_SOURCE_QUESTIONS:
    answer = agent.ask(question)
    print(f"问题: {question}")
    print(f"相关文档数: {len(answer.relevant_docs)}")
    print(f"来源: {answer.sources}")
    print(f"置信度: {answer.confidence:.2%}\n")
```

## ⚠️ 注意事项

### 1. 版权问题

- ✅ **官方网站**: 全国人大、最高法、政府网站通常可以合理使用
- ⚠️ **商业网站**: 注意版权声明，仅供个人学习使用
- ❌ **付费内容**: 不要抓取需要付费订阅的内容

### 2. 反爬虫

某些网站有反爬虫机制：

```python
# 在 scraper/web_scraper.py 中配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 ...',
    'Referer': 'https://example.com/',
    'Accept': 'text/html,application/xhtml+xml',
}

# 添加延迟
await asyncio.sleep(2)  # 每次请求间隔2秒
```

### 3. 成本控制

添加大量文档会增加成本：

```python
# 估算成本
documents = 100            # 新增文档数
avg_length = 2000         # 平均长度（字符）
tokens = documents * avg_length * 1.5  # 约300K tokens

embedding_cost = tokens / 1_000_000 * 0.02  # ~$0.006
storage_cost = 0  # FAISS本地存储，无成本

print(f"预估成本: ${embedding_cost:.4f}")
```

### 4. 性能影响

文档数量增加会影响检索速度：

| 文档数 | 检索时间 | 内存占用 |
|-------|---------|---------|
| 100 | <0.1s | ~10MB |
| 1000 | <0.5s | ~100MB |
| 10000 | ~1s | ~1GB |
| 100000 | ~5s | ~10GB |

**优化建议**:
- 使用FAISS的IVF索引（更快）
- 过滤低质量文档
- 定期清理过期内容

## 📝 完整示例

### 示例: 添加劳动合同法全文

```bash
# 步骤1: 编辑配置
nano config.py
# 添加URL: "http://www.npc.gov.cn/npc/c30834/202101/bfe9b0eb39c04124a4a52e1a2ef11eb8.shtml"

# 步骤2: 重新构建
python -m legal_rights build-kb --force

# 步骤3: 验证
python -m legal_rights ask "劳动合同法第三十九条规定了什么？" --verbose

# 步骤4: 查看统计
python -m legal_rights stats
```

预期结果：
- total_documents: 37 → 60+ (增加约20-30个文档块)
- 新问题的置信度提升
- 可以检索到法律条文的精确内容

## 🎯 推荐的扩展计划

### 阶段1: 补充核心法规（优先）

1. ✅ 劳动合同法全文
2. ✅ 劳动法全文
3. ✅ 劳动争议调解仲裁法
4. ✅ 社会保险法

**预期提升**:
- 文档数: 37 → 100+
- 法律依据问题置信度: 40% → 80%

### 阶段2: 添加司法解释（中期）

1. ✅ 最高法劳动争议司法解释（一~四）
2. ✅ 最高检相关解释

**预期提升**:
- 文档数: 100 → 150+
- 复杂案例问题置信度: 50% → 75%

### 阶段3: 扩展地方政策（可选）

1. ✅ 北京、上海、广东、深圳等主要城市
2. ✅ 各地人社局官方解读

**预期提升**:
- 覆盖全国主要城市
- 地方政策问题准确度提升

### 阶段4: 增加判例（高级）

1. ✅ 从裁判文书网抓取典型案例
2. ✅ 整理分类

**预期提升**:
- 案例分析能力
- 可以给出类似判例参考

## 📚 参考资源

- [全国人大法律数据库](http://www.npc.gov.cn/)
- [最高人民法院](https://www.court.gov.cn/)
- [中国裁判文书网](https://wenshu.court.gov.cn/)
- [各地人社部门](https://www.12333.gov.cn/)

---

**文档版本**: 1.0
**创建日期**: 2026-02-06
**适用版本**: legal_rights v1.0.2+
