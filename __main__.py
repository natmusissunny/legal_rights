"""
法律维权智能助手 - CLI入口
"""
import argparse
import sys
import asyncio
from pathlib import Path

from .config import Config
from .env_loader import print_api_key_status


def main():
    """CLI主入口"""
    parser = argparse.ArgumentParser(
        prog="python -m legal_rights",
        description="法律维权智能助手 - 专注于离职员工劳动法维权问答",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 构建知识库
  python -m legal_rights build-kb

  # 单次问答
  python -m legal_rights ask "公司恶意辞退不给补偿怎么办？"

  # 交互式对话
  python -m legal_rights chat

  # 测试API连接
  python -m legal_rights test

  # 显示知识库统计
  python -m legal_rights stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # build-kb 命令
    parser_build = subparsers.add_parser(
        "build-kb",
        help="构建知识库（抓取网页、生成文档、构建向量索引）"
    )
    parser_build.add_argument(
        "--force",
        action="store_true",
        help="强制重新构建（忽略缓存）"
    )
    parser_build.add_argument(
        "--skip-scrape",
        action="store_true",
        help="跳过网页抓取（使用现有缓存）"
    )

    # ask 命令
    parser_ask = subparsers.add_parser(
        "ask",
        help="单次问答"
    )
    parser_ask.add_argument(
        "question",
        type=str,
        help="要提问的问题"
    )
    parser_ask.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细信息（包括检索的文档片段）"
    )
    parser_ask.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="检索文档数量（默认5）"
    )

    # chat 命令
    parser_chat = subparsers.add_parser(
        "chat",
        help="交互式对话模式"
    )
    parser_chat.add_argument(
        "--reset",
        action="store_true",
        help="清空对话历史重新开始"
    )

    # test 命令
    parser_test = subparsers.add_parser(
        "test",
        help="测试API连接"
    )

    # stats 命令
    parser_stats = subparsers.add_parser(
        "stats",
        help="显示知识库统计信息"
    )

    args = parser.parse_args()

    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 验证配置
    if not Config.validate():
        print("\n❌ 配置验证失败！")
        print("\n请按照以下步骤配置API密钥：")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中填入您的 CLAUDE_API_KEY 和 OPENAI_API_KEY")
        print("\n或者设置环境变量：")
        print("   export CLAUDE_API_KEY=your-claude-key")
        print("   export OPENAI_API_KEY=your-openai-key")
        print("\n提示：查看 docs/SETUP_GUIDE.md 获取详细配置说明")
        sys.exit(1)

    # 执行命令
    try:
        if args.command == "build-kb":
            build_knowledge_base(force=args.force, skip_scrape=args.skip_scrape)
        elif args.command == "ask":
            ask_question(args.question, verbose=args.verbose, top_k=args.top_k)
        elif args.command == "chat":
            start_chat(reset=args.reset)
        elif args.command == "test":
            test_api_connection()
        elif args.command == "stats":
            show_stats()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def build_knowledge_base(force: bool = False, skip_scrape: bool = False):
    """构建知识库"""
    from .scraper import WebScraper, HTMLCleaner, ContentParser
    from .knowledge import TextGenerator, VectorIndexer

    print("\n🏗️  开始构建知识库")
    print("=" * 80)

    structured_contents = []

    # 步骤1: 网页抓取
    if not skip_scrape:
        print("\n[步骤 1/4] 抓取网页内容")
        print("-" * 80)

        scraper = WebScraper()
        use_cache = not force

        try:
            results = asyncio.run(scraper.fetch_target_urls(use_cache=use_cache))

            if not any(results.values()):
                print("\n⚠️  所有网页抓取失败")
                print("提示: 可能是网站反爬虫，请查看 scripts/manual_scrape_guide.md")
                print("或使用 --skip-scrape 跳过抓取步骤（使用现有缓存）")
                return

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return
    else:
        print("\n[步骤 1/4] 跳过网页抓取（使用缓存）")
        print("-" * 80)
        print("✅ 已跳过")

    # 步骤2: 内容解析
    print("\n[步骤 2/4] 解析和清洗内容")
    print("-" * 80)

    cleaner = HTMLCleaner()
    parser = ContentParser()

    # 读取缓存的HTML
    cache_files = list(Config.CACHE_DIR.glob("*.html"))
    if not cache_files:
        print("❌ 没有找到缓存的HTML文件")
        print("请先运行不带 --skip-scrape 的命令，或手动添加HTML到 data/cache/")
        return

    print(f"找到 {len(cache_files)} 个缓存文件")

    for i, cache_file in enumerate(cache_files, 1):
        print(f"\n  [{i}/{len(cache_files)}] {cache_file.name}")

        try:
            html = cache_file.read_text(encoding='utf-8')
            cleaned_html, text = cleaner.clean_and_extract(html)

            # 尝试从文件名或内容提取标题
            title = f"法律文档 {i}"

            structured = parser.parse(
                html=cleaned_html,
                url=f"file://{cache_file}",
                title=title
            )

            structured_contents.append(structured)
            print(f"      ✅ 解析完成 ({len(structured.sections)} 个章节)")

        except Exception as e:
            print(f"      ❌ 解析失败: {e}")

    if not structured_contents:
        print("\n❌ 没有成功解析任何内容")
        return

    print(f"\n✅ 成功解析 {len(structured_contents)} 个文档")

    # 步骤3: 生成文档
    print("\n[步骤 3/4] 生成Markdown文档")
    print("-" * 80)

    generator = TextGenerator()
    try:
        generator.generate_batch(structured_contents, format='md')
    except Exception as e:
        print(f"❌ 文档生成失败: {e}")
        return

    # 步骤4: 构建向量索引
    print("\n[步骤 4/4] 构建向量索引")
    print("-" * 80)

    try:
        indexer = VectorIndexer()
        indexer.build_index(structured_contents, show_progress=True)
        indexer.save_index()
    except Exception as e:
        print(f"❌ 索引构建失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 完成
    print("\n" + "=" * 80)
    print("🎉 知识库构建完成！")
    print("=" * 80)
    print("\n现在可以使用以下命令:")
    print("  python -m legal_rights ask \"你的问题\"")
    print("  python -m legal_rights chat")


def ask_question(question: str, verbose: bool = False, top_k: int = 5):
    """单次问答"""
    from .agent import LegalAgent

    print("\n💬 法律维权智能助手")
    print("=" * 80)

    # 检查索引
    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("\n⚠️  向量索引不存在")
        print("请先运行: python -m legal_rights build-kb")
        return

    # 初始化Agent
    try:
        agent = LegalAgent()
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return

    # 问答
    try:
        answer = agent.ask(question, use_context=False, top_k=top_k)

        # 显示答案
        print("\n" + "=" * 80)
        print(answer.display())

        # 详细模式
        if verbose and answer.relevant_docs:
            print("\n" + "=" * 80)
            print("📚 相关文档片段")
            print("=" * 80)

            for i, doc in enumerate(answer.relevant_docs, 1):
                print(f"\n文档 {i}:")
                print(f"  章节: {doc.section_title}")
                print(f"  内容: {doc.content[:200]}...")

    except Exception as e:
        print(f"\n❌ 回答失败: {e}")
        import traceback
        traceback.print_exc()


def start_chat(reset: bool = False):
    """交互式对话"""
    from .agent import LegalAgent

    print("\n💬 法律维权智能助手 - 交互式对话")
    print("=" * 80)
    print("提示:")
    print("  - 输入问题并按回车")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'reset' 重置对话历史")
    print("  - 输入 'summary' 查看对话摘要")
    print("=" * 80)

    # 检查索引
    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("\n⚠️  向量索引不存在")
        print("请先运行: python -m legal_rights build-kb")
        return

    # 初始化Agent
    try:
        agent = LegalAgent()
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return

    if reset:
        agent.reset_conversation()
        print("\n✅ 对话历史已重置")

    print("\n开始对话...\n")

    turn = 0

    while True:
        try:
            # 获取用户输入
            user_input = input(f"\n[{turn}] 您: ").strip()

            if not user_input:
                continue

            # 特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break

            if user_input.lower() == 'reset':
                agent.reset_conversation()
                turn = 0
                print("✅ 对话历史已重置")
                continue

            if user_input.lower() == 'summary':
                summary = agent.get_conversation_summary()
                print("\n📊 对话摘要:")
                print("-" * 80)
                print(summary)
                continue

            # 问答
            turn += 1
            print(f"\n[{turn}] 助手: ", end="", flush=True)

            answer = agent.chat(user_input)

            # 流式显示（模拟）
            print(answer.answer_text)

            # 显示置信度
            if answer.confidence < 0.7:
                print(f"\n⚠️  置信度较低 ({answer.confidence:.0%})，建议咨询专业律师")

        except KeyboardInterrupt:
            print("\n\n👋 对话已结束")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            continue


def test_api_connection():
    """测试API连接"""
    from .agent.llm_factory import create_llm_client
    from .knowledge.embedding_factory import create_embedding_client

    print("\n🔍 测试API连接")
    print("=" * 80)

    # 显示API密钥状态
    print("\n[1] API密钥状态")
    print("-" * 80)
    print_api_key_status()

    # 测试 LLM API
    print("\n[2] 测试 LLM API")
    print("-" * 80)

    try:
        llm_client = create_llm_client()
        print("正在调用LLM API...", end=" ", flush=True)

        response = llm_client.complete(
            prompt="请用一句话说明什么是经济补偿金。",
            system="你是劳动法律师。",
            temperature=0.5,
            max_tokens=100
        )

        print("✅ 成功")
        print(f"响应: {response[:100]}...")

    except Exception as e:
        print(f"❌ 失败")
        print(f"错误: {e}")

    # 测试 Embedding API
    print("\n[3] 测试 Embedding API")
    print("-" * 80)

    try:
        embedding_client = create_embedding_client()
        print("正在生成向量...", end=" ", flush=True)

        embedding = embedding_client.embed("测试文本")

        print("✅ 成功")
        print(f"向量维度: {len(embedding)}")
        print(f"向量前5维: {embedding[:5]}")

    except Exception as e:
        print(f"❌ 失败")
        print(f"错误: {e}")

    print("\n" + "=" * 80)
    print("测试完成")


def show_stats():
    """显示知识库统计"""
    import json

    print("\n📊 知识库统计信息")
    print("=" * 80)

    # 检查数据目录
    cache_dir = Config.CACHE_DIR
    knowledge_dir = Config.KNOWLEDGE_DIR
    vectors_dir = Config.VECTORS_DIR

    cache_files = list(cache_dir.glob("*.html")) if cache_dir.exists() else []
    doc_files = list(knowledge_dir.glob("*")) if knowledge_dir.exists() else []
    vector_files = list(vectors_dir.glob("*")) if vectors_dir.exists() else []

    print(f"\n📁 数据目录:")
    print(f"  - 缓存目录: {cache_dir}")
    print(f"    HTML文件: {len(cache_files)}")

    print(f"  - 文档目录: {knowledge_dir}")
    print(f"    Markdown: {len(list(knowledge_dir.glob('*.md')))}")
    print(f"    文本文件: {len(list(knowledge_dir.glob('*.txt')))}")

    print(f"  - 向量目录: {vectors_dir}")
    print(f"    文件数: {len(vector_files)}")

    # 读取向量统计
    stats_file = vectors_dir / "stats.json"
    if stats_file.exists():
        print(f"\n📈 向量索引统计:")
        try:
            stats = json.loads(stats_file.read_text(encoding='utf-8'))
            print(f"  - 文档数: {stats.get('total_documents', 0)}")
            print(f"  - 向量维度: {stats.get('vector_dimension', 0)}")
            print(f"  - 索引类型: {stats.get('index_type', 'N/A')}")
            print(f"  - 数据源数: {len(stats.get('sources', []))}")
            print(f"  - 章节数: {len(stats.get('sections', []))}")
        except Exception as e:
            print(f"  ⚠️  读取统计失败: {e}")

    # 状态判断
    print(f"\n🎯 知识库状态:")

    if len(cache_files) == 0:
        print("  ❌ 未抓取网页")
        print("     运行: python -m legal_rights build-kb")
    elif len(doc_files) == 0:
        print("  ⚠️  已抓取但未生成文档")
        print("     运行: python -m legal_rights build-kb --skip-scrape")
    elif len(vector_files) == 0:
        print("  ⚠️  已生成文档但未构建索引")
        print("     运行: python -m legal_rights build-kb --skip-scrape")
    else:
        print("  ✅ 知识库完整")
        print("     可以使用: python -m legal_rights ask \"问题\"")


if __name__ == "__main__":
    main()
