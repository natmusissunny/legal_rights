"""
测试网页抓取模块
完整测试：抓取 → 清洗 → 解析
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.scraper import WebScraper, HTMLCleaner, ContentParser
from legal_rights.config import Config


async def test_full_pipeline():
    """测试完整的抓取流程"""
    print("🧪 测试网页抓取模块")
    print("=" * 80)

    # 初始化组件
    scraper = WebScraper()
    cleaner = HTMLCleaner()
    parser = ContentParser()

    # 1. 抓取网页
    print("\n[步骤1] 抓取目标网页")
    print("-" * 80)
    results = await scraper.fetch_target_urls(use_cache=True)

    # 2. 清洗和解析
    print("\n[步骤2] 清洗和解析内容")
    print("-" * 80)

    structured_contents = []

    for url, html in results.items():
        if not html:
            print(f"❌ 跳过失败的URL: {url}")
            continue

        print(f"\n处理: {url}")
        print("-" * 60)

        # 清洗HTML
        cleaned_html, text = cleaner.clean_and_extract(html)
        print(f"  ✅ 清洗完成")
        print(f"     原始长度: {len(html):,} 字符")
        print(f"     清洗后长度: {len(cleaned_html):,} 字符")
        print(f"     纯文本长度: {len(text):,} 字符")

        # 解析结构
        structured = parser.parse(cleaned_html, url)
        structured_contents.append(structured)

        print(f"  ✅ 解析完成")
        print(f"     标题: {structured.title}")
        print(f"     章节数: {len(structured.sections)}")
        print(f"     抓取时间: {structured.scraped_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # 显示章节结构
        if structured.sections:
            print(f"\n  📋 章节结构:")
            _print_sections(structured.sections, indent=2)

    # 3. 统计
    print("\n" + "=" * 80)
    print("📊 统计信果")
    print("=" * 80)
    print(f"总URL数: {len(Config.TARGET_URLS)}")
    print(f"抓取成功: {len([h for h in results.values() if h])}")
    print(f"解析完成: {len(structured_contents)}")

    total_sections = sum(len(sc.sections) for sc in structured_contents)
    print(f"总章节数: {total_sections}")

    return structured_contents


def _print_sections(sections, indent=0):
    """递归打印章节结构"""
    for section in sections:
        prefix = "    " * indent
        content_preview = section.content[:80].replace('\n', ' ') if section.content else "(无内容)"
        print(f"{prefix}├─ [Lv{section.level}] {section.title}")
        print(f"{prefix}│  {content_preview}...")

        if section.subsections:
            _print_sections(section.subsections, indent + 1)


async def test_single_url():
    """测试单个URL"""
    test_url = Config.TARGET_URLS[0]

    print(f"🧪 测试单个URL: {test_url}")
    print("=" * 80)

    scraper = WebScraper()
    cleaner = HTMLCleaner()
    parser = ContentParser()

    # 抓取
    print("\n[1] 抓取网页...")
    html = await scraper.fetch(test_url, use_cache=True)

    if not html:
        print("❌ 抓取失败")
        return

    print(f"✅ 抓取成功 ({len(html):,} 字符)")

    # 清洗
    print("\n[2] 清洗HTML...")
    cleaned_html, text = cleaner.clean_and_extract(html)
    print(f"✅ 清洗完成")
    print(f"   清洗后: {len(cleaned_html):,} 字符")
    print(f"   纯文本: {len(text):,} 字符")

    # 解析
    print("\n[3] 解析内容...")
    structured = parser.parse(cleaned_html, test_url)
    print(f"✅ 解析完成")
    print(f"   标题: {structured.title}")
    print(f"   章节数: {len(structured.sections)}")

    # 显示详细结构
    print("\n[4] 内容预览:")
    print("-" * 80)
    print(f"标题: {structured.title}")
    print(f"URL: {structured.url}")
    print(f"抓取时间: {structured.scraped_at}")
    print()

    if structured.sections:
        print("章节结构:")
        _print_sections(structured.sections, indent=0)
    else:
        print("(未找到章节结构)")

    # 显示文本预览
    print("\n[5] 文本预览 (前500字):")
    print("-" * 80)
    print(text[:500])
    if len(text) > 500:
        print("...")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="测试网页抓取模块")
    parser.add_argument(
        '--mode',
        choices=['full', 'single'],
        default='full',
        help='测试模式: full=完整测试, single=单个URL'
    )

    args = parser.parse_args()

    if args.mode == 'full':
        asyncio.run(test_full_pipeline())
    else:
        asyncio.run(test_single_url())


if __name__ == "__main__":
    main()
