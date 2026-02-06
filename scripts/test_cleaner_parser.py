"""
测试HTML清洗和内容解析
使用示例HTML文件
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.scraper import HTMLCleaner, ContentParser


def main():
    """主测试函数"""
    print("🧪 测试 HTML 清洗和内容解析")
    print("=" * 80)

    # 读取示例HTML
    sample_html_path = project_root / "data" / "cache" / "sample_legal_content.html"

    if not sample_html_path.exists():
        print(f"❌ 示例文件不存在: {sample_html_path}")
        return

    print(f"\n📄 读取示例文件: {sample_html_path.name}")
    html = sample_html_path.read_text(encoding='utf-8')
    print(f"   原始长度: {len(html):,} 字符")

    # 测试 HTML 清洗
    print("\n" + "-" * 80)
    print("[步骤1] HTML 清洗")
    print("-" * 80)

    cleaner = HTMLCleaner()
    cleaned_html, text = cleaner.clean_and_extract(html)

    print(f"✅ 清洗完成")
    print(f"   清洗后 HTML 长度: {len(cleaned_html):,} 字符")
    print(f"   提取文本长度: {len(text):,} 字符")
    print(f"   压缩率: {(1 - len(cleaned_html)/len(html)) * 100:.1f}%")

    # 显示文本预览
    print(f"\n📝 提取的文本预览 (前300字):")
    print("-" * 60)
    print(text[:300])
    if len(text) > 300:
        print("...")

    # 测试内容解析
    print("\n" + "-" * 80)
    print("[步骤2] 内容解析")
    print("-" * 80)

    parser = ContentParser()
    structured = parser.parse(
        html=cleaned_html,
        url="https://example.com/sample",
        title=None
    )

    print(f"✅ 解析完成")
    print(f"   文档标题: {structured.title}")
    print(f"   来源URL: {structured.url}")
    print(f"   抓取时间: {structured.scraped_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   顶层章节数: {len(structured.sections)}")

    # 统计总章节数
    def count_sections(sections):
        count = len(sections)
        for section in sections:
            count += count_sections(section.subsections)
        return count

    total_sections = count_sections(structured.sections)
    print(f"   总章节数: {total_sections}")

    # 显示章节结构
    print(f"\n📚 章节结构:")
    print("-" * 60)
    print_section_tree(structured.sections, indent=0)

    # 显示详细内容
    print("\n" + "-" * 80)
    print("[步骤3] 详细内容展示")
    print("-" * 80)

    if structured.sections:
        first_section = structured.sections[0]
        print(f"\n示例章节: {first_section.title}")
        print(f"层级: {first_section.level}")
        print(f"内容长度: {len(first_section.content)} 字符")
        print(f"子章节数: {len(first_section.subsections)}")
        print(f"\n内容预览:")
        print("-" * 60)
        content_preview = first_section.content[:400]
        print(content_preview)
        if len(first_section.content) > 400:
            print("...")

    # 测试关键词提取
    print("\n" + "-" * 80)
    print("[步骤4] 关键词提取")
    print("-" * 80)

    keywords = parser.extract_keywords(text)
    print(f"✅ 提取到 {len(keywords)} 个关键词:")
    print(", ".join(keywords[:15]))  # 显示前15个

    print("\n" + "=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)


def print_section_tree(sections, indent=0):
    """打印章节树形结构"""
    for i, section in enumerate(sections):
        prefix = "│   " * indent + "├── "
        if i == len(sections) - 1:
            prefix = "│   " * indent + "└── "

        # 内容预览
        content_preview = ""
        if section.content:
            preview_text = section.content[:50].replace('\n', ' ')
            content_preview = f" [{preview_text}...]"

        print(f"{prefix}[Lv{section.level}] {section.title}{content_preview}")

        if section.subsections:
            print_section_tree(section.subsections, indent + 1)


if __name__ == "__main__":
    main()
