#!/usr/bin/env python3
"""
自动获取核心法律法规脚本
一键下载劳动法、劳动合同法等核心法规
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.scraper import WebScraper
from legal_rights.config import Config


# 核心法律法规URL列表
CORE_LAWS = {
    "劳动合同法": {
        "url": "http://www.npc.gov.cn/npc/c30834/202101/bfe9b0eb39c04124a4a52e1a2ef11eb8.shtml",
        "source": "全国人大",
        "priority": 1,
        "description": "《中华人民共和国劳动合同法》全文"
    },
    "劳动法": {
        "url": "http://www.npc.gov.cn/npc/c238/202101/5f9f098fa72f4337962af793e8c08867.shtml",
        "source": "全国人大",
        "priority": 1,
        "description": "《中华人民共和国劳动法》全文"
    },
    "劳动争议调解仲裁法": {
        "url": "http://www.npc.gov.cn/npc/c238/200712/ec1cdb6b6fe148938e5a5b6ca0b06caa.shtml",
        "source": "全国人大",
        "priority": 1,
        "description": "《中华人民共和国劳动争议调解仲裁法》全文"
    },
    "社会保险法": {
        "url": "http://www.npc.gov.cn/npc/c238/201010/1e8d191aeb234396b1b7147f7bbea7bd.shtml",
        "source": "全国人大",
        "priority": 1,
        "description": "《中华人民共和国社会保险法》全文"
    },
    "工伤保险条例": {
        "url": "http://www.gov.cn/zwgk/2010-12/24/content_1771066.htm",
        "source": "国务院",
        "priority": 2,
        "description": "《工伤保险条例》全文"
    },
    "劳动保障监察条例": {
        "url": "http://www.gov.cn/gongbao/content/2004/content_62976.htm",
        "source": "国务院",
        "priority": 2,
        "description": "《劳动保障监察条例》全文"
    },
    "最高法劳动争议司法解释一": {
        "url": "https://www.court.gov.cn/fabu-xiangqing-13012.html",
        "source": "最高人民法院",
        "priority": 2,
        "description": "最高人民法院关于审理劳动争议案件适用法律问题的解释（一）"
    },
    "职工带薪年休假条例": {
        "url": "http://www.gov.cn/zwgk/2007-12/16/content_836496.htm",
        "source": "国务院",
        "priority": 3,
        "description": "《职工带薪年休假条例》全文"
    },
}


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_law_info(name: str, info: dict):
    """打印法规信息"""
    print(f"\n📜 {name}")
    print(f"   来源: {info['source']}")
    print(f"   优先级: {'🔴 高' if info['priority'] == 1 else '🟡 中' if info['priority'] == 2 else '🟢 低'}")
    print(f"   说明: {info['description']}")
    print(f"   URL: {info['url']}")


async def fetch_laws(priority_filter: int = None, dry_run: bool = False, auto_confirm: bool = False):
    """
    获取法律法规

    Args:
        priority_filter: 优先级过滤（1=高优先级, 2=中优先级, 3=低优先级）
        dry_run: 仅显示信息，不实际下载
    """
    print_header("🏛️  核心法律法规自动获取工具")

    print(f"\n📊 可用法规总数: {len(CORE_LAWS)}")

    # 过滤法规
    if priority_filter:
        filtered_laws = {
            name: info for name, info in CORE_LAWS.items()
            if info['priority'] <= priority_filter
        }
        print(f"📌 根据优先级过滤后: {len(filtered_laws)} 个法规")
    else:
        filtered_laws = CORE_LAWS

    # 显示法规列表
    print("\n" + "-" * 80)
    print("将获取以下法规:")
    print("-" * 80)

    for name, info in filtered_laws.items():
        print_law_info(name, info)

    if dry_run:
        print("\n💡 这是预览模式，未实际下载")
        print("   运行 python scripts/fetch_core_laws.py --download 开始下载")
        return

    # 确认
    print("\n" + "=" * 80)
    print(f"⚠️  即将下载 {len(filtered_laws)} 个法规文件")
    print("=" * 80)

    if not auto_confirm:
        print("\n确认下载? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice != 'y':
                print("❌ 已取消")
                return False
        except EOFError:
            print("\n⚠️  检测到非交互环境，自动确认")
            auto_confirm = True

    if auto_confirm:
        print("\n✅ 自动确认下载")

    # 下载
    print("\n" + "=" * 80)
    print("开始下载...")
    print("=" * 80)

    scraper = WebScraper()
    urls = [info['url'] for info in filtered_laws.values()]

    # 批量下载
    results = await scraper.fetch_all(urls, use_cache=False)

    # 统计结果
    success_count = sum(1 for html in results.values() if html)
    fail_count = len(results) - success_count

    print("\n" + "=" * 80)
    print("下载完成!")
    print("=" * 80)
    print(f"\n✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")

    if fail_count > 0:
        print(f"\n⚠️  部分文件下载失败，可能原因:")
        print(f"   1. 网络连接问题")
        print(f"   2. 网站反爬虫限制")
        print(f"   3. URL已失效")
        print(f"\n💡 建议:")
        print(f"   - 稍后重试")
        print(f"   - 使用手动下载方法（见下方说明）")

    # 显示缓存位置
    print(f"\n📁 文件已保存到: {Config.CACHE_DIR}")
    print(f"   查看: ls -lh {Config.CACHE_DIR}/*.html")

    # 下一步提示
    print("\n" + "=" * 80)
    print("🎯 下一步:")
    print("=" * 80)
    print("\n1️⃣  重新构建知识库（整合新法规）:")
    print("   python -m legal_rights build-kb --force")
    print("\n2️⃣  验证效果:")
    print("   python -m legal_rights stats")
    print("   python -m legal_rights ask \"劳动合同法第三十九条规定了什么？\"")

    return True


def show_manual_download_guide():
    """显示手动下载指南"""
    print_header("📖 手动下载指南")

    print("\n如果自动下载失败，您可以手动下载：")
    print("\n" + "=" * 80)

    for i, (name, info) in enumerate(CORE_LAWS.items(), 1):
        if info['priority'] == 1:  # 只显示高优先级
            print(f"\n{i}. {name}")
            print(f"   ├─ 访问: {info['url']}")
            print(f"   ├─ 右键 → 另存为 → 保存为 HTML")
            print(f"   └─ 保存到: {Config.CACHE_DIR}/{name}.html")

    print("\n" + "=" * 80)
    print("\n保存完成后，运行:")
    print("   python -m legal_rights build-kb --skip-scrape")
    print("\n💡 使用 --skip-scrape 参数可跳过网页抓取，直接使用已保存的HTML文件")


def check_current_status():
    """检查当前知识库状态"""
    print_header("📊 当前知识库状态")

    # 检查缓存文件
    cache_files = list(Config.CACHE_DIR.glob("*.html"))
    print(f"\n📁 缓存文件数: {len(cache_files)}")

    if cache_files:
        print(f"   最新文件: {cache_files[-1].name}")
        print(f"   最后更新: {datetime.fromtimestamp(cache_files[-1].stat().st_mtime)}")

    # 检查知识库文件
    knowledge_files = list(Config.KNOWLEDGE_DIR.glob("*.md"))
    print(f"\n📚 知识库文档: {len(knowledge_files)}")

    # 检查向量索引
    index_file = Config.VECTORS_DIR / "index.faiss"
    stats_file = Config.VECTORS_DIR / "stats.json"

    if index_file.exists():
        import json
        if stats_file.exists():
            stats = json.loads(stats_file.read_text())
            print(f"\n🔍 向量索引:")
            print(f"   文档块数: {stats.get('total_documents', 0)}")
            print(f"   数据源数: {len(stats.get('sources', []))}")
            print(f"   章节数: {len(stats.get('sections', []))}")
    else:
        print(f"\n⚠️  向量索引未构建")

    # 建议
    print("\n" + "=" * 80)
    if len(cache_files) < 7:  # 当前3个 + 新增4个 = 7个
        print("💡 建议: 下载核心法规以提升知识库质量")
        print("   运行: python scripts/fetch_core_laws.py --download")
    else:
        print("✅ 缓存文件充足，可以重新构建知识库")
        print("   运行: python -m legal_rights build-kb --force")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="自动获取核心法律法规",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看可用法规列表
  python scripts/fetch_core_laws.py --list

  # 仅下载高优先级法规（4个核心法规）
  python scripts/fetch_core_laws.py --priority 1 --download

  # 下载所有法规
  python scripts/fetch_core_laws.py --download --all

  # 检查当前状态
  python scripts/fetch_core_laws.py --status

  # 显示手动下载指南
  python scripts/fetch_core_laws.py --manual
        """
    )

    parser.add_argument('--list', action='store_true',
                      help='显示可用法规列表（不下载）')
    parser.add_argument('--download', action='store_true',
                      help='开始下载')
    parser.add_argument('--priority', type=int, choices=[1, 2, 3],
                      help='按优先级过滤 (1=高, 2=中, 3=低)')
    parser.add_argument('--all', action='store_true',
                      help='下载所有法规（忽略优先级）')
    parser.add_argument('--status', action='store_true',
                      help='检查当前知识库状态')
    parser.add_argument('--manual', action='store_true',
                      help='显示手动下载指南')
    parser.add_argument('--yes', '-y', action='store_true',
                      help='自动确认，不提示（用于脚本调用）')

    args = parser.parse_args()

    # 如果没有指定任何选项，显示列表
    if not any([args.list, args.download, args.status, args.manual]):
        args.list = True

    # 执行操作
    if args.status:
        check_current_status()
    elif args.manual:
        show_manual_download_guide()
    elif args.list:
        priority = None if args.all else (args.priority or 1)
        asyncio.run(fetch_laws(priority_filter=priority, dry_run=True))
    elif args.download:
        priority = None if args.all else (args.priority or 1)
        asyncio.run(fetch_laws(priority_filter=priority, dry_run=False, auto_confirm=args.yes))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
