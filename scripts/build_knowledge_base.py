"""
一键构建知识库脚本
自动化完成从抓取到索引的全部流程
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.config import Config
from legal_rights.scraper import WebScraper, HTMLCleaner, ContentParser
from legal_rights.knowledge import TextGenerator, VectorIndexer


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_step(step_num: int, total_steps: int, title: str):
    """打印步骤标题"""
    print(f"\n[步骤 {step_num}/{total_steps}] {title}")
    print("-" * 80)


async def main():
    """主函数"""
    print_header("🏗️  法律维权知识库构建工具")

    # 检查API密钥
    print("\n检查配置...")
    if not Config.OPENAI_API_KEY:
        print("❌ 错误: 未配置 OPENAI_API_KEY")
        print("请在 .env 文件中配置 API 密钥")
        sys.exit(1)

    print("✅ 配置检查通过")

    # 步骤1: 抓取网页
    print_step(1, 4, "抓取网页内容")

    scraper = WebScraper()
    results = await scraper.fetch_target_urls(use_cache=True)

    successful_urls = [url for url, html in results.items() if html]
    if not successful_urls:
        print("\n❌ 所有网页抓取失败")
        print("提示: 网站可能有反爬虫，请手动下载HTML到 data/cache/")
        print("或运行: python -m legal_rights build-kb --skip-scrape")

        # 检查是否有缓存
        cache_files = list(Config.CACHE_DIR.glob("*.html"))
        if cache_files:
            print(f"\n✅ 发现 {len(cache_files)} 个缓存文件，将继续处理")
        else:
            sys.exit(1)

    # 步骤2: 解析内容
    print_step(2, 4, "解析和清洗内容")

    cleaner = HTMLCleaner()
    parser = ContentParser()

    # 读取所有HTML文件
    cache_files = list(Config.CACHE_DIR.glob("*.html"))
    print(f"找到 {len(cache_files)} 个HTML文件")

    structured_contents = []

    for i, cache_file in enumerate(cache_files, 1):
        print(f"\n  [{i}/{len(cache_files)}] 处理: {cache_file.name}")

        try:
            html = cache_file.read_text(encoding='utf-8')
            cleaned_html, text = cleaner.clean_and_extract(html)

            # 从元数据文件读取URL（如果存在）
            meta_file = cache_file.with_suffix('.meta')
            url = f"file://{cache_file}"
            if meta_file.exists():
                meta_content = meta_file.read_text(encoding='utf-8')
                for line in meta_content.split('\n'):
                    if line.startswith('url='):
                        url = line.split('=', 1)[1].strip()
                        break

            # 提取标题
            title = f"法律文档 {i}"
            temp_parser = ContentParser()
            temp_soup = __import__('bs4').BeautifulSoup(cleaned_html, 'lxml')
            extracted_title = temp_parser._extract_title(temp_soup)
            if extracted_title != "未命名文档":
                title = extracted_title

            structured = parser.parse(
                html=cleaned_html,
                url=url,
                title=title
            )

            structured_contents.append(structured)
            print(f"      ✅ 解析完成")
            print(f"         标题: {title}")
            print(f"         章节: {len(structured.sections)}")

        except Exception as e:
            print(f"      ❌ 解析失败: {e}")
            continue

    if not structured_contents:
        print("\n❌ 没有成功解析任何内容")
        sys.exit(1)

    print(f"\n✅ 成功解析 {len(structured_contents)} 个文档")

    # 步骤3: 生成文档
    print_step(3, 4, "生成Markdown文档")

    generator = TextGenerator()
    doc_paths = generator.generate_batch(structured_contents, format='md')

    print(f"\n✅ 生成了 {len(doc_paths)} 个Markdown文档")

    # 步骤4: 构建向量索引
    print_step(4, 4, "构建向量索引")

    try:
        indexer = VectorIndexer()
        indexer.build_index(structured_contents, show_progress=True)
        indexer.save_index()
    except Exception as e:
        print(f"\n❌ 索引构建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 完成
    print_header("🎉 知识库构建完成！")

    print("\n📊 构建摘要:")
    print(f"  - 处理文档: {len(structured_contents)}")
    print(f"  - 生成文档: {len(doc_paths)}")
    print(f"  - 索引文档块: {len(indexer.documents)}")
    print(f"  - 向量维度: {indexer.dimension}")

    print("\n💡 下一步:")
    print("  python -m legal_rights ask \"你的问题\"")
    print("  python -m legal_rights chat")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
