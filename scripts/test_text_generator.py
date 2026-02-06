"""
测试文本文档生成器
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.scraper import HTMLCleaner, ContentParser
from legal_rights.knowledge import TextGenerator
from legal_rights.config import Config


def main():
    """测试文本生成"""
    print("🧪 测试文本文档生成器")
    print("=" * 80)

    # 读取示例HTML
    sample_html_path = project_root / "data" / "cache" / "sample_legal_content.html"

    if not sample_html_path.exists():
        print(f"❌ 示例文件不存在: {sample_html_path}")
        return

    print(f"\n[步骤1] 读取示例HTML")
    html = sample_html_path.read_text(encoding='utf-8')
    print(f"   ✅ 读取完成 ({len(html):,} 字符)")

    # 清洗和解析
    print(f"\n[步骤2] 清洗和解析内容")
    cleaner = HTMLCleaner()
    parser = ContentParser()

    cleaned_html, text = cleaner.clean_and_extract(html)
    print(f"   ✅ 清洗完成 ({len(text):,} 字符)")

    structured = parser.parse(
        html=cleaned_html,
        url="https://example.com/sample",
        title="离职经济补偿指南"
    )
    print(f"   ✅ 解析完成 ({len(structured.sections)} 个章节)")

    # 生成Markdown文档
    print(f"\n[步骤3] 生成Markdown文档")
    print("-" * 80)
    generator = TextGenerator()
    md_path = generator.generate(structured, format='md')

    # 生成纯文本文档
    print(f"\n[步骤4] 生成纯文本文档")
    print("-" * 80)
    txt_path = generator.generate(structured, format='txt')

    # 显示结果
    print("\n" + "=" * 80)
    print("✅ 文档生成完成!")
    print("=" * 80)

    print(f"\n📁 Markdown文件:")
    print(f"   路径: {md_path}")
    print(f"   大小: {md_path.stat().st_size:,} 字节")

    print(f"\n📁 纯文本文件:")
    print(f"   路径: {txt_path}")
    print(f"   大小: {txt_path.stat().st_size:,} 字节")

    # 显示Markdown预览
    print(f"\n📝 Markdown文档预览 (前50行):")
    print("-" * 80)
    md_content = md_path.read_text(encoding='utf-8')
    lines = md_content.split('\n')[:50]
    for line in lines:
        print(line)
    if len(md_content.split('\n')) > 50:
        print("...")

    print(f"\n💡 查看完整文档:")
    print(f"   cat \"{md_path}\"")
    print(f"   cat \"{txt_path}\"")


if __name__ == "__main__":
    main()
