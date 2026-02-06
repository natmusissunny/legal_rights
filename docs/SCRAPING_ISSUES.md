# 🕷️ 网页抓取问题处理指南

## 常见错误码

### HTTP 412 - Precondition Failed

**现象**:
```
❌ HTTP错误 412: https://m12333.cn/qa/myyuf.html
```

**原因**:
- 网站检测到自动化请求特征
- 缺少必要的请求头（Referer、Cookie等）
- 访问频率过快触发限制

**解决方案**:

#### 方案1: 手动下载（推荐）

1. 用浏览器打开该URL
2. 按 `Ctrl+S` (Windows) 或 `Cmd+S` (Mac) 保存网页
3. 将保存的 `.html` 文件复制到 `data/cache/` 目录
4. 重命名为对应的MD5哈希值:

```bash
# 计算URL的MD5
python3 -c "import hashlib; print(hashlib.md5('https://m12333.cn/qa/myyuf.html'.encode()).hexdigest())"
# 输出: 例如 abc123def456...

# 重命名文件
mv ~/Downloads/page.html data/cache/abc123def456.html
```

#### 方案2: 使用代理

如果有代理服务器，可以在代码中配置:

```python
# 修改 scraper/web_scraper.py 的 fetch 方法
async with httpx.AsyncClient(
    timeout=30.0,
    follow_redirects=True,
    proxies="http://your-proxy:port"  # 添加这一行
) as client:
    ...
```

#### 方案3: 更换数据源

如果某个网站持续失败，可以替换为其他类似内容的网站:

```python
# 修改 config.py 中的 TARGET_URLS
TARGET_URLS = [
    "https://alternative-site-1.com/...",
    "https://alternative-site-2.com/...",
    "https://alternative-site-3.com/...",
]
```

### HTTP 404 - Not Found

**现象**:
```
❌ HTTP错误 404: https://sh.bendibao.com/2022831/258695.shtm
```

**原因**:
- 页面已被删除
- URL已更改
- 文章已下线

**解决方案**:

1. 在浏览器中验证URL是否有效
2. 如果页面确实不存在，从配置中移除该URL:

```python
# 编辑 config.py
TARGET_URLS = [
    # "https://sh.bendibao.com/2022831/258695.shtm",  # 注释掉失效的URL
    "https://m12333.cn/qa/myyuf.html",
    "https://www.hshfy.sh.cn/...",
]
```

3. 寻找替代页面:
   - 在该网站搜索相关主题
   - 使用百度搜索: `site:bendibao.com 离职补偿`

### HTTP 502/503 - Server Error

**现象**:
```
❌ HTTP错误 502: https://sh.bendibao.com/...
```

**原因**:
- 网站服务器临时故障
- 网站维护中
- 服务器负载过高

**解决方案**:

1. **等待后重试**:
```bash
# 等待 5-10 分钟后重新执行
sleep 300 && python -m legal_rights build-kb
```

2. **使用已有缓存**:
如果之前抓取成功过，可以使用缓存的内容:
```bash
# 检查缓存目录
ls -lh data/cache/

# 查看缓存元数据
cat data/cache/*.meta
```

## 🎯 最佳实践

### 1. 先使用缓存

```bash
# build-kb 默认使用缓存，失败的URL才会重新抓取
python -m legal_rights build-kb
```

### 2. 手动下载难抓取的页面

对于持续失败的网站，建议手动下载:

```bash
# 1. 浏览器打开并保存页面
# 2. 计算MD5哈希
python3 -c "
import hashlib
url = 'https://m12333.cn/qa/myyuf.html'
print(hashlib.md5(url.encode()).hexdigest())
"

# 3. 复制文件到缓存目录
cp ~/Downloads/page.html data/cache/<MD5值>.html

# 4. 创建元数据文件
echo "url=https://m12333.cn/qa/myyuf.html" > data/cache/<MD5值>.meta
echo "timestamp=$(date -Iseconds)" >> data/cache/<MD5值>.meta

# 5. 重新构建知识库
python -m legal_rights build-kb
```

### 3. 分批抓取

如果多个URL同时失败，可以一个一个来:

```python
# 临时修改 config.py
TARGET_URLS = [
    "https://www.hshfy.sh.cn/...",  # 先抓这一个
]

# 抓取成功后，再添加下一个
TARGET_URLS = [
    "https://www.hshfy.sh.cn/...",
    "https://m12333.cn/...",  # 添加第二个
]
```

### 4. 使用本地文件

如果你已经有相关的PDF或HTML文件:

```bash
# 方法1: 直接放入 data/knowledge/ 目录
cp your-file.pdf data/knowledge/

# 方法2: 放入缓存目录（需要计算MD5）
# 见上面的"手动下载"说明
```

## 🔧 高级配置

### 增加重试次数

编辑 `scraper/web_scraper.py`:

```python
async def fetch(
    self,
    url: str,
    use_cache: bool = True,
    max_retries: int = 5  # 从 3 改为 5
) -> Optional[str]:
    ...
```

### 增加请求间隔

编辑 `config.py`:

```python
# 降低抓取频率（从 4 次/秒 降低到 1 次/秒）
RATE_LIMIT_PER_SECOND = 1
```

### 添加更多请求头

编辑 `scraper/web_scraper.py`，在 `fetch` 方法的 headers 中添加:

```python
headers = {
    ...
    "Cookie": "your-cookie-here",  # 从浏览器复制
    "Referer": "https://www.baidu.com/",  # 模拟从百度搜索进入
}
```

## 📊 诊断工具

### 检查缓存状态

```bash
# 查看所有缓存文件
python -m legal_rights check-cache

# 或手动查看
ls -lh data/cache/
cat data/cache/*.meta
```

### 测试单个URL

```python
# 创建测试脚本 test_url.py
import asyncio
from scraper import WebScraper

async def test():
    scraper = WebScraper()
    url = "https://m12333.cn/qa/myyuf.html"
    html = await scraper.fetch(url, use_cache=False, max_retries=5)
    if html:
        print(f"✅ 成功: {len(html)} 字符")
    else:
        print("❌ 失败")

asyncio.run(test())
```

### 模拟浏览器请求

使用 `curl` 测试:

```bash
curl -v \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -H "Referer: https://www.baidu.com/" \
  -H "Accept: text/html" \
  "https://m12333.cn/qa/myyuf.html"
```

## 🚨 当所有方法都失败时

### 方案A: 跳过失败的URL

```python
# 编辑 config.py，注释掉失败的URL
TARGET_URLS = [
    # "https://m12333.cn/qa/myyuf.html",  # 持续失败，暂时跳过
    "https://www.hshfy.sh.cn/...",  # 这个成功了
]
```

### 方案B: 使用备用数据源

```python
# 添加更容易抓取的替代网站
TARGET_URLS = [
    "https://www.gov.cn/...",  # 政府网站通常更稳定
    "https://www.chinanews.com/...",  # 新闻网站
    "https://baike.baidu.com/...",  # 百度百科
]
```

### 方案C: 手动构建知识库

1. 收集相关PDF/Word文档
2. 转换为文本文件
3. 直接放入 `data/knowledge/` 目录
4. 运行索引构建:

```bash
python -m legal_rights build-kb --skip-scraping
```

## 💡 总结

**按优先级推荐的解决方案**:

1. ✅ **使用缓存** - 如果之前抓取成功过
2. ✅ **手动下载** - 最可靠，适用于少量页面
3. ✅ **更换数据源** - 寻找更容易抓取的网站
4. ⚠️  **配置代理** - 需要额外资源
5. ⚠️  **修改代码** - 需要技术能力

**记住**:
- 反爬虫是正常现象，不是代码问题
- 手动下载是最可靠的方法
- 有缓存就优先使用缓存
- 实在不行就换个数据源

---

**相关文档**:
- FAQ.md - 常见问题
- QUICK_START.md - 快速开始指南
- config.py - 配置文件说明
