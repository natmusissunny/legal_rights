#!/usr/bin/env python3
"""
手动将HTML文件添加到缓存
用于处理无法自动抓取的网页
"""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.config import Config


def calculate_md5(url: str) -> str:
    """计算URL的MD5哈希"""
    return hashlib.md5(url.encode()).hexdigest()


def add_to_cache(url: str, html_file: Path):
    """
    将HTML文件添加到缓存

    Args:
        url: 原始URL
        html_file: HTML文件路径
    """
    if not html_file.exists():
        print(f"❌ 文件不存在: {html_file}")
        return False

    # 计算缓存路径
    url_hash = calculate_md5(url)
    cache_path = Config.CACHE_DIR / f"{url_hash}.html"
    meta_path = Config.CACHE_DIR / f"{url_hash}.meta"

    try:
        # 读取HTML内容
        html_content = html_file.read_text(encoding='utf-8')

        # 保存到缓存
        cache_path.write_text(html_content, encoding='utf-8')

        # 保存元数据
        metadata = f"url={url}\ntimestamp={datetime.now().isoformat()}\nmanual=true\n"
        meta_path.write_text(metadata, encoding='utf-8')

        print(f"✅ 已添加到缓存")
        print(f"   URL: {url}")
        print(f"   缓存文件: {cache_path}")
        print(f"   大小: {len(html_content):,} 字符")

        return True

    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False


def main():
    """主函数"""
    print("📦 手动添加HTML到缓存")
    print("=" * 70)

    # 解析命令行参数
    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python scripts/add_to_cache.py <URL> <HTML文件路径>")
        print("\n示例:")
        print("  python scripts/add_to_cache.py \\")
        print('    "https://m12333.cn/qa/myyuf.html" \\')
        print("    ~/Downloads/page.html")
        print("\n说明:")
        print("  1. 用浏览器打开目标URL")
        print("  2. 按 Ctrl+S (Win) 或 Cmd+S (Mac) 保存网页")
        print("  3. 运行此脚本将保存的文件添加到缓存")
        print("  4. 重新执行 python -m legal_rights build-kb")
        return

    url = sys.argv[1]
    html_file = Path(sys.argv[2]).expanduser()

    print(f"\nURL: {url}")
    print(f"文件: {html_file}")
    print(f"MD5: {calculate_md5(url)}")
    print()

    # 添加到缓存
    if add_to_cache(url, html_file):
        print("\n" + "=" * 70)
        print("✅ 完成! 现在可以运行:")
        print("   python -m legal_rights build-kb")
    else:
        print("\n" + "=" * 70)
        print("❌ 添加失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
