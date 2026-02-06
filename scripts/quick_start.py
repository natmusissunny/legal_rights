"""
快速开始脚本
引导用户完成初始设置和首次使用
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.config import Config
from legal_rights.env_loader import print_api_key_status


def print_header(title: str, width: int = 80):
    """打印标题"""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_step(step_num: int, title: str, width: int = 80):
    """打印步骤"""
    print(f"\n{'─' * width}")
    print(f"步骤 {step_num}: {title}")
    print('─' * width)


def check_environment():
    """检查环境"""
    print("\n检查Python版本...", end=" ")
    import sys
    if sys.version_info < (3, 10):
        print(f"❌")
        print(f"   当前版本: Python {sys.version_info.major}.{sys.version_info.minor}")
        print(f"   需要: Python 3.10+")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    print("检查依赖包...", end=" ")
    required_packages = [
        'anthropic',
        'openai',
        'faiss',
        'pydantic',
        'httpx',
        'beautifulsoup4'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("❌")
        print(f"   缺失: {', '.join(missing)}")
        print(f"   运行: pip install -r requirements.txt")
        return False

    print("✅")
    return True


def check_api_keys():
    """检查API密钥"""
    print("\n检查API密钥配置...")
    print_api_key_status()

    has_claude = Config.CLAUDE_API_KEY is not None
    has_openai = Config.OPENAI_API_KEY is not None

    if not has_claude or not has_openai:
        print("\n⚠️  API密钥配置不完整")
        return False

    return True


def check_knowledge_base():
    """检查知识库"""
    print("\n检查知识库...", end=" ")

    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("❌ 未构建")
        return False

    print("✅ 已构建")

    # 显示统计
    import json
    stats_file = Config.VECTORS_DIR / "stats.json"
    if stats_file.exists():
        stats = json.loads(stats_file.read_text(encoding='utf-8'))
        print(f"   文档数: {stats.get('total_documents', 0)}")
        print(f"   章节数: {len(stats.get('sections', []))}")

    return True


def interactive_setup():
    """交互式设置"""
    print("\n是否现在配置API密钥? (y/n): ", end="")
    choice = input().strip().lower()

    if choice == 'y':
        print("\n请编辑 .env 文件并添加以下内容:")
        print("-" * 80)
        print("CLAUDE_API_KEY=sk-ant-api03-your-key-here")
        print("OPENAI_API_KEY=sk-your-key-here")
        print("-" * 80)

        env_path = Config.PROJECT_ROOT / ".env"
        if not env_path.exists():
            example_path = Config.PROJECT_ROOT / ".env.example"
            if example_path.exists():
                import shutil
                shutil.copy(example_path, env_path)
                print(f"\n✅ 已创建 .env 文件: {env_path}")
                print("请编辑该文件并填入您的API密钥")
            else:
                print(f"\n请手动创建 .env 文件: {env_path}")

        print("\n配置完成后，重新运行此脚本")
        return False

    return True


def main():
    """主函数"""
    print_header("🚀 法律维权智能助手 - 快速开始")

    print("\n欢迎使用法律维权智能助手！")
    print("本脚本将引导您完成初始设置和首次使用。")

    # 步骤1: 检查环境
    print_step(1, "检查运行环境")

    if not check_environment():
        print("\n❌ 环境检查失败")
        print("请先安装必要的依赖:")
        print("  pip install -r requirements.txt")
        return False

    print("\n✅ 环境检查通过")

    # 步骤2: 检查API密钥
    print_step(2, "检查API密钥")

    if not check_api_keys():
        print("\n请按照以下步骤配置API密钥:")
        print("  1. 获取Claude API密钥: https://console.anthropic.com/")
        print("  2. 获取OpenAI API密钥: https://platform.openai.com/")
        print("  3. 将密钥添加到 .env 文件")
        print("\n详细说明请查看: docs/SETUP_GUIDE.md")

        if not interactive_setup():
            return False

    print("\n✅ API密钥配置完成")

    # 步骤3: 检查知识库
    print_step(3, "检查知识库")

    kb_ready = check_knowledge_base()

    if not kb_ready:
        print("\n知识库尚未构建。")
        print("\n是否现在构建知识库? (y/n): ", end="")
        choice = input().strip().lower()

        if choice == 'y':
            print("\n开始构建知识库...")
            print("运行命令: python -m legal_rights build-kb")
            print("\n注意: 此过程需要3-5分钟，并会调用API产生少量费用 (<$0.01)")
            print("\n请在命令行运行:")
            print("  python -m legal_rights build-kb")
            return False
        else:
            print("\n稍后可以运行以下命令构建知识库:")
            print("  python -m legal_rights build-kb")
            return False

    print("\n✅ 知识库已就绪")

    # 步骤4: 完成设置
    print_step(4, "设置完成")

    print("\n🎉 恭喜！所有设置已完成，可以开始使用了。")

    print("\n📚 快速开始:")
    print("  1. 单次问答:")
    print("     python -m legal_rights ask \"如何计算N+1补偿？\"")
    print("\n  2. 交互式对话:")
    print("     python -m legal_rights chat")
    print("\n  3. 查看帮助:")
    print("     python -m legal_rights --help")

    print("\n📖 文档:")
    print("  - CLI使用指南: docs/CLI_GUIDE.md")
    print("  - Agent指南: docs/AGENT_GUIDE.md")
    print("  - 配置指南: docs/SETUP_GUIDE.md")

    print("\n💡 示例问题:")
    print("  - 公司恶意辞退不给补偿怎么办？")
    print("  - 工作3年月薪8000元，被辞退应该赔多少？")
    print("  - 劳动仲裁需要准备什么材料？")

    print("\n是否现在开始提问? (y/n): ", end="")
    choice = input().strip().lower()

    if choice == 'y':
        print("\n💬 请输入您的问题: ", end="")
        question = input().strip()

        if question:
            print("\n正在查询...")
            print(f"\n运行命令: python -m legal_rights ask \"{question}\"")
            print("\n请在命令行运行以上命令获取答案。")

    print("\n" + "=" * 80)
    print("感谢使用法律维权智能助手！".center(80))
    print("=" * 80)

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
