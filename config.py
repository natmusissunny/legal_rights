"""
配置管理模块
"""
from pathlib import Path
from typing import Optional
from .env_loader import get_claude_api_key, get_openai_api_key, get_rate_limit


class Config:
    """项目配置类"""

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = DATA_DIR / "cache"
    KNOWLEDGE_DIR = DATA_DIR / "knowledge"
    VECTORS_DIR = DATA_DIR / "vectors"

    # 目标URL列表
    TARGET_URLS = [
        "https://m12333.cn/qa/myyuf.html",
        "https://www.hshfy.sh.cn/shfy/web/xxnr.jsp?pa=aaWQ9MjAxNzcwODUmeGg9MSZsbWRtPWxtNTE5z&zd=xwzx",
        "https://sh.bendibao.com/zffw/2022831/258695.shtm",
    ]

    # API配置
    CLAUDE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    RATE_LIMIT_PER_SECOND: int = 4

    # 向量检索配置
    CHUNK_SIZE: int = 512  # 文档分块大小（tokens）
    CHUNK_OVERLAP: int = 50  # 分块重叠大小（tokens）
    TOP_K_RESULTS: int = 5  # 检索返回Top-K结果
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # OpenAI embedding模型

    # Claude配置
    # 推荐使用: claude-sonnet-4-5 (最新Sonnet，性价比最高)
    # 或: claude-opus-4-6 (最强模型，成本较高)
    CLAUDE_MODEL: str = "claude-sonnet-4-5"  # Claude模型 (2026年最新)
    MAX_TOKENS: int = 2000  # 最大生成token数

    @classmethod
    def load(cls):
        """加载配置（从环境变量或.env文件）"""
        cls.CLAUDE_API_KEY = get_claude_api_key()
        cls.OPENAI_API_KEY = get_openai_api_key()
        cls.RATE_LIMIT_PER_SECOND = get_rate_limit(default=4)

        # 确保数据目录存在
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTORS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> bool:
        """验证必需的配置是否已设置"""
        if not cls.CLAUDE_API_KEY:
            print("❌ 错误: 未配置 CLAUDE_API_KEY")
            return False
        if not cls.OPENAI_API_KEY:
            print("❌ 错误: 未配置 OPENAI_API_KEY")
            return False
        return True


# 自动加载配置
Config.load()
