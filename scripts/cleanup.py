"""
清理脚本
清理缓存、临时文件和生成的数据
"""
import sys
from pathlib import Path
import shutil

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.config import Config


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def get_dir_size(path: Path) -> int:
    """获取目录大小（字节）"""
    if not path.exists():
        return 0

    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total


def format_size(size: int) -> str:
    """格式化大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def show_status():
    """显示当前状态"""
    print_header("📊 当前数据状态")

    dirs = {
        "缓存 (cache)": Config.CACHE_DIR,
        "文档 (knowledge)": Config.KNOWLEDGE_DIR,
        "向量 (vectors)": Config.VECTORS_DIR,
    }

    total_size = 0

    for name, path in dirs.items():
        if path.exists():
            files = list(path.glob("*"))
            size = get_dir_size(path)
            total_size += size

            print(f"\n{name}:")
            print(f"  路径: {path}")
            print(f"  文件数: {len(files)}")
            print(f"  大小: {format_size(size)}")
        else:
            print(f"\n{name}:")
            print(f"  状态: 目录不存在")

    print(f"\n总大小: {format_size(total_size)}")


def clean_cache(confirm: bool = True):
    """清理缓存"""
    cache_dir = Config.CACHE_DIR

    if not cache_dir.exists():
        print("✅ 缓存目录不存在，无需清理")
        return

    files = list(cache_dir.glob("*"))
    size = get_dir_size(cache_dir)

    print(f"\n将删除缓存:")
    print(f"  文件数: {len(files)}")
    print(f"  大小: {format_size(size)}")

    if confirm:
        print("\n确认删除? (y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("已取消")
            return

    # 删除文件
    for file in files:
        try:
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
        except Exception as e:
            print(f"  ⚠️  删除失败: {file.name} - {e}")

    print(f"✅ 已清理 {len(files)} 个文件")


def clean_knowledge(confirm: bool = True):
    """清理生成的文档"""
    knowledge_dir = Config.KNOWLEDGE_DIR

    if not knowledge_dir.exists():
        print("✅ 文档目录不存在，无需清理")
        return

    files = list(knowledge_dir.glob("*"))
    size = get_dir_size(knowledge_dir)

    print(f"\n将删除文档:")
    print(f"  文件数: {len(files)}")
    print(f"  大小: {format_size(size)}")

    if confirm:
        print("\n确认删除? (y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("已取消")
            return

    # 删除文件
    for file in files:
        try:
            if file.is_file():
                file.unlink()
        except Exception as e:
            print(f"  ⚠️  删除失败: {file.name} - {e}")

    print(f"✅ 已清理 {len(files)} 个文件")


def clean_vectors(confirm: bool = True):
    """清理向量索引"""
    vectors_dir = Config.VECTORS_DIR

    if not vectors_dir.exists():
        print("✅ 向量目录不存在，无需清理")
        return

    files = list(vectors_dir.glob("*"))
    size = get_dir_size(vectors_dir)

    print(f"\n将删除向量索引:")
    print(f"  文件数: {len(files)}")
    print(f"  大小: {format_size(size)}")

    if confirm:
        print("\n⚠️  删除向量索引后需要重新构建知识库！")
        print("确认删除? (y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("已取消")
            return

    # 删除文件
    for file in files:
        try:
            if file.is_file():
                file.unlink()
        except Exception as e:
            print(f"  ⚠️  删除失败: {file.name} - {e}")

    print(f"✅ 已清理 {len(files)} 个文件")


def clean_all(confirm: bool = True):
    """清理所有数据"""
    total_size = (
        get_dir_size(Config.CACHE_DIR) +
        get_dir_size(Config.KNOWLEDGE_DIR) +
        get_dir_size(Config.VECTORS_DIR)
    )

    print(f"\n⚠️  将删除所有数据!")
    print(f"总大小: {format_size(total_size)}")

    if confirm:
        print("\n这将删除缓存、文档和向量索引。")
        print("确认删除? (y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("已取消")
            return

    print("\n清理中...")
    clean_cache(confirm=False)
    clean_knowledge(confirm=False)
    clean_vectors(confirm=False)

    print("\n✅ 所有数据已清理")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="清理数据和缓存",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看当前状态
  python scripts/cleanup.py --status

  # 清理缓存
  python scripts/cleanup.py --cache

  # 清理所有数据
  python scripts/cleanup.py --all

  # 清理所有数据（不确认）
  python scripts/cleanup.py --all --yes
        """
    )

    parser.add_argument('--status', action='store_true', help='显示当前状态')
    parser.add_argument('--cache', action='store_true', help='清理缓存')
    parser.add_argument('--knowledge', action='store_true', help='清理文档')
    parser.add_argument('--vectors', action='store_true', help='清理向量索引')
    parser.add_argument('--all', action='store_true', help='清理所有数据')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认')

    args = parser.parse_args()

    print_header("🧹 数据清理工具")

    # 如果没有指定任何选项，显示帮助
    if not any([args.status, args.cache, args.knowledge, args.vectors, args.all]):
        show_status()
        print("\n💡 使用 --help 查看清理选项")
        return True

    # 显示状态
    if args.status:
        show_status()
        return True

    # 清理操作
    confirm = not args.yes

    if args.all:
        clean_all(confirm=confirm)
    else:
        if args.cache:
            clean_cache(confirm=confirm)
        if args.knowledge:
            clean_knowledge(confirm=confirm)
        if args.vectors:
            clean_vectors(confirm=confirm)

    # 显示清理后状态
    show_status()

    print("\n💡 重建知识库:")
    print("  python -m legal_rights build-kb")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
