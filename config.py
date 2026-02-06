"""
配置管理模块
"""
from pathlib import Path
from typing import Optional
from .env_loader import get_api_key, get_rate_limit, load_env_file


class Config:
    """项目配置类"""

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = DATA_DIR / "cache"
    KNOWLEDGE_DIR = DATA_DIR / "knowledge"
    VECTORS_DIR = DATA_DIR / "vectors"

    # 目标URL列表
    # 提示: 如果某个URL抓取失败（HTTP 412/404等），可以:
    #   1. 手动下载: python scripts/add_to_cache.py "<URL>" <文件路径>
    #   2. 跳过该URL: 将下面对应的行注释掉（在前面加 #）
    #   3. 详细说明: 参见 docs/SCRAPING_ISSUES.md
    TARGET_URLS = [
        "https://m12333.cn/qa/myyuf.html",  # 12333劳动保障咨询
        "https://www.hshfy.sh.cn/shfy/web/xxnr.jsp?pa=aaWQ9MjAxNzcwODUmeGg9MSZsbWRtPWxtNTE5z&zd=xwzx",  # 上海高院
        "https://sh.bendibao.com/2022831/258695.shtm",  # 本地宝
    ]

    # LLM模式选择: 'claude', 'qwen', 'zhipu'
    LLM_MODE: str = "auto"  # auto 会根据配置的API密钥自动选择

    # API配置
    CLAUDE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DASHSCOPE_API_KEY: Optional[str] = None  # 通义千问
    ZHIPUAI_API_KEY: Optional[str] = None    # 智谱AI

    RATE_LIMIT_PER_SECOND: int = 4

    # 向量检索配置
    CHUNK_SIZE: int = 512  # 文档分块大小（tokens）
    CHUNK_OVERLAP: int = 50  # 分块重叠大小（tokens）
    TOP_K_RESULTS: int = 5  # 检索返回Top-K结果
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # OpenAI embedding模型
    ZHIPU_EMBEDDING_MODEL: str = "embedding-2"  # 智谱AI embedding模型

    # Claude配置
    CLAUDE_MODEL: str = "claude-sonnet-4-5"  # Claude模型 (2026年最新)

    # 通义千问配置
    QWEN_MODEL: str = "qwen-max"  # qwen-max, qwen-plus, qwen-turbo

    # 智谱AI配置
    ZHIPU_MODEL: str = "glm-4"  # glm-4, glm-4-plus

    MAX_TOKENS: int = 2000  # 最大生成token数

    @classmethod
    def load(cls):
        """加载配置（从环境变量或.env文件）"""
        # 加载所有可能的API密钥
        cls.CLAUDE_API_KEY = get_api_key('CLAUDE_API_KEY')
        cls.OPENAI_API_KEY = get_api_key('OPENAI_API_KEY')
        cls.DASHSCOPE_API_KEY = get_api_key('DASHSCOPE_API_KEY')
        cls.ZHIPUAI_API_KEY = get_api_key('ZHIPUAI_API_KEY')
        cls.RATE_LIMIT_PER_SECOND = get_rate_limit(default=4)

        # 加载LLM模式配置
        env_vars = load_env_file()
        if 'LLM_MODE' in env_vars:
            cls.LLM_MODE = env_vars['LLM_MODE'].lower()

        # 确保数据目录存在
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTORS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def auto_select_llm(cls) -> str:
        """自动选择可用的LLM"""
        if cls.LLM_MODE != "auto":
            return cls.LLM_MODE

        # 优先级：国内大模型 > Claude
        if cls.DASHSCOPE_API_KEY:
            return "qwen"
        elif cls.ZHIPUAI_API_KEY:
            return "zhipu"
        elif cls.CLAUDE_API_KEY:
            return "claude"
        else:
            return None

    @classmethod
    def auto_select_embedding(cls) -> str:
        """自动选择可用的Embedding"""
        # 优先级：智谱AI > OpenAI
        if cls.ZHIPUAI_API_KEY:
            return "zhipu"
        elif cls.OPENAI_API_KEY:
            return "openai"
        else:
            return None

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        验证必需的配置是否已设置

        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []

        # 检查LLM配置
        llm_mode = cls.auto_select_llm()
        if not llm_mode:
            errors.append("未配置任何LLM API密钥（CLAUDE_API_KEY / DASHSCOPE_API_KEY / ZHIPUAI_API_KEY）")

        # 检查Embedding配置
        embedding_mode = cls.auto_select_embedding()
        if not embedding_mode:
            errors.append("未配置任何Embedding API密钥（OPENAI_API_KEY / ZHIPUAI_API_KEY）")

        return len(errors) == 0, errors

    @classmethod
    def print_status(cls):
        """打印配置状态"""
        print("\n" + "="*60)
        print("📊 当前配置状态")
        print("="*60)

        # LLM配置
        print("\n🤖 大语言模型 (LLM):")
        if cls.CLAUDE_API_KEY:
            masked = cls.CLAUDE_API_KEY[:12] + '...' + cls.CLAUDE_API_KEY[-4:]
            print(f"  ✅ Claude API: {masked}")
        else:
            print(f"  ❌ Claude API: 未配置")

        if cls.DASHSCOPE_API_KEY:
            masked = cls.DASHSCOPE_API_KEY[:7] + '...' + cls.DASHSCOPE_API_KEY[-4:]
            print(f"  ✅ 通义千问 API: {masked}")
        else:
            print(f"  ❌ 通义千问 API: 未配置")

        if cls.ZHIPUAI_API_KEY:
            masked = cls.ZHIPUAI_API_KEY[:7] + '...' if len(cls.ZHIPUAI_API_KEY) > 10 else '***'
            print(f"  ✅ 智谱AI API: {masked}")
        else:
            print(f"  ❌ 智谱AI API: 未配置")

        # Embedding配置
        print("\n🔢 向量化模型 (Embedding):")
        if cls.OPENAI_API_KEY:
            masked = cls.OPENAI_API_KEY[:7] + '...' + cls.OPENAI_API_KEY[-4:]
            print(f"  ✅ OpenAI API: {masked}")
        else:
            print(f"  ❌ OpenAI API: 未配置")

        if cls.ZHIPUAI_API_KEY:
            print(f"  ✅ 智谱AI Embedding: 可用")
        else:
            print(f"  ❌ 智谱AI Embedding: 未配置")

        # 自动选择结果
        print("\n🎯 自动选择结果:")
        llm_mode = cls.auto_select_llm()
        if llm_mode:
            llm_names = {"claude": "Claude", "qwen": "通义千问", "zhipu": "智谱AI"}
            print(f"  LLM: {llm_names.get(llm_mode, llm_mode)}")
        else:
            print(f"  LLM: ❌ 无可用配置")

        embedding_mode = cls.auto_select_embedding()
        if embedding_mode:
            emb_names = {"openai": "OpenAI", "zhipu": "智谱AI"}
            print(f"  Embedding: {emb_names.get(embedding_mode, embedding_mode)}")
        else:
            print(f"  Embedding: ❌ 无可用配置")

        print("\n" + "="*60)

        # 验证配置
        is_valid, errors = cls.validate()
        if not is_valid:
            print("\n❌ 配置验证失败！\n")
            for error in errors:
                print(f"  • {error}")
            print("\n💡 配置指南:")
            print("  1. 复制 .env.example 为 .env")
            print("  2. 在 .env 中填入至少一组API密钥:")
            print("     • Claude + OpenAI（国际版）")
            print("     • 通义千问 + 智谱AI（国内版，推荐）")
            print("  3. 或设置环境变量")
            print("\n详见: docs/SETUP_GUIDE.md")
        else:
            print("\n✅ 配置验证通过！")


# 自动加载配置
Config.load()
