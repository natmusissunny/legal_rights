"""
网页抓取器
使用 httpx 异步抓取目标网页，支持缓存和重试
"""
import asyncio
import hashlib
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import httpx
from ..config import Config


class WebScraper:
    """网页抓取器"""

    def __init__(self):
        """初始化抓取器"""
        self.cache_dir = Config.CACHE_DIR
        self.rate_limit = Config.RATE_LIMIT_PER_SECOND
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self._last_request_time = 0

    async def _wait_for_rate_limit(self):
        """等待速率限制"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self._last_request_time = asyncio.get_event_loop().time()

    def _get_cache_path(self, url: str) -> Path:
        """获取缓存文件路径"""
        # 使用 URL 的 MD5 作为文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def _get_cache_metadata_path(self, url: str) -> Path:
        """获取缓存元数据路径"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.meta"

    def _load_from_cache(self, url: str) -> Optional[str]:
        """从缓存加载HTML"""
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            try:
                return cache_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️  读取缓存失败: {e}")
                return None
        return None

    def _save_to_cache(self, url: str, html: str):
        """保存HTML到缓存"""
        cache_path = self._get_cache_path(url)
        meta_path = self._get_cache_metadata_path(url)

        try:
            # 保存 HTML 内容
            cache_path.write_text(html, encoding='utf-8')

            # 保存元数据
            metadata = f"url={url}\ntimestamp={datetime.now().isoformat()}\n"
            meta_path.write_text(metadata, encoding='utf-8')

            print(f"✅ 已缓存: {url}")
        except Exception as e:
            print(f"⚠️  保存缓存失败: {e}")

    async def fetch(
        self,
        url: str,
        use_cache: bool = True,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        抓取单个网页

        Args:
            url: 目标URL
            use_cache: 是否使用缓存
            max_retries: 最大重试次数

        Returns:
            HTML内容，失败返回None
        """
        # 尝试从缓存加载
        if use_cache:
            cached_html = self._load_from_cache(url)
            if cached_html:
                print(f"📦 使用缓存: {url}")
                return cached_html

        # 抓取网页
        print(f"🌐 抓取中: {url}")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

        for attempt in range(max_retries):
            try:
                # 等待速率限制
                await self._wait_for_rate_limit()

                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()

                    # 尝试多种编码
                    html = None
                    for encoding in ['utf-8', 'gb2312', 'gbk']:
                        try:
                            html = response.content.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue

                    if html is None:
                        # 使用 chardet 自动检测（如果可用）
                        try:
                            import chardet
                            detected = chardet.detect(response.content)
                            html = response.content.decode(detected['encoding'])
                        except:
                            # 最后使用默认编码并忽略错误
                            html = response.content.decode('utf-8', errors='ignore')

                    # 保存到缓存
                    self._save_to_cache(url, html)

                    print(f"✅ 抓取成功: {url} ({len(html)} 字符)")
                    return html

            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP错误 {e.response.status_code}: {url}")
                if e.response.status_code in [404, 403, 401]:
                    # 不重试这些错误
                    return None
            except httpx.TimeoutException:
                print(f"⏱️  请求超时 (尝试 {attempt + 1}/{max_retries}): {url}")
            except Exception as e:
                print(f"❌ 抓取失败 (尝试 {attempt + 1}/{max_retries}): {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"⏳ 等待 {wait_time}s 后重试...")
                await asyncio.sleep(wait_time)

        print(f"❌ 抓取最终失败: {url}")
        return None

    async def fetch_all(
        self,
        urls: List[str],
        use_cache: bool = True,
        max_retries: int = 3
    ) -> dict[str, Optional[str]]:
        """
        批量抓取多个网页

        Args:
            urls: URL列表
            use_cache: 是否使用缓存
            max_retries: 最大重试次数

        Returns:
            字典 {url: html_content}
        """
        print(f"\n🚀 开始批量抓取 {len(urls)} 个网页...")
        print("=" * 60)

        tasks = [self.fetch(url, use_cache, max_retries) for url in urls]
        results = await asyncio.gather(*tasks)

        result_dict = dict(zip(urls, results))

        # 统计结果
        success_count = sum(1 for html in results if html is not None)
        print("\n" + "=" * 60)
        print(f"📊 抓取完成: 成功 {success_count}/{len(urls)}")

        return result_dict

    async def fetch_target_urls(
        self,
        use_cache: bool = True
    ) -> dict[str, Optional[str]]:
        """
        抓取配置中的目标URL

        Args:
            use_cache: 是否使用缓存

        Returns:
            字典 {url: html_content}
        """
        return await self.fetch_all(Config.TARGET_URLS, use_cache)


async def main():
    """测试函数"""
    scraper = WebScraper()

    # 测试抓取目标URL
    results = await scraper.fetch_target_urls(use_cache=True)

    print("\n📋 抓取结果:")
    print("=" * 60)
    for url, html in results.items():
        if html:
            print(f"✅ {url}")
            print(f"   长度: {len(html)} 字符")
        else:
            print(f"❌ {url}")
            print(f"   状态: 失败")


if __name__ == "__main__":
    asyncio.run(main())
