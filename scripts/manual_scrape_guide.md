# 手动抓取指南

由于目标网站具有反爬虫机制（返回 412/304 状态码），自动抓取可能失败。以下是手动保存网页的步骤：

## 方法 1: 浏览器手动保存

1. 在浏览器中打开目标URL
2. 等待页面完全加载
3. 右键 → "Save Page As" / "另存为"
4. 选择 "Webpage, Complete" / "网页，全部"
5. 保存到 `data/cache/` 目录，文件名为URL的MD5哈希值

### 目标URLs和对应的文件名

```bash
# URL 1: https://m12333.cn/qa/myyuf.html
# MD5: d41d8cd98f00b204e9800998ecf8427e (示例)
# 保存为: data/cache/d41d8cd98f00b204e9800998ecf8427e.html

# URL 2: https://www.hshfy.sh.cn/shfy/web/xxnr.jsp?pa=aaWQ9MjAxNzcwODUmeGg9MSZsbWRtPWxtNTE5z&zd=xwzx
# MD5: (计算对应的MD5)
# 保存为: data/cache/{md5}.html

# URL 3: https://sh.bendibao.com/zffw/2022831/258695.shtm
# MD5: (计算对应的MD5)
# 保存为: data/cache/{md5}.html
```

### 计算URL的MD5

```python
import hashlib

url = "https://m12333.cn/qa/myyuf.html"
md5_hash = hashlib.md5(url.encode()).hexdigest()
print(f"{url} -> {md5_hash}.html")
```

## 方法 2: 使用 wget 或 curl

```bash
# 使用 wget
wget -O data/cache/{md5}.html "https://example.com/page"

# 使用 curl
curl -o data/cache/{md5}.html "https://example.com/page"
```

## 方法 3: 使用 Selenium (推荐用于生产环境)

如果需要自动化抓取，建议使用 Selenium：

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)
html = driver.page_source
driver.quit()

# 保存 html 到缓存
```

## 元数据文件

同时创建对应的 `.meta` 文件：

```
url=https://m12333.cn/qa/myyuf.html
timestamp=2026-02-06T11:30:00
```

## 注意事项

1. 尊重网站的 robots.txt 和服务条款
2. 避免高频请求，影响网站正常运营
3. 仅用于学习和个人使用
4. 缓存的内容可能过时，需要定期更新
