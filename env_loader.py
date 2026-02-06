"""
环境变量和配置加载器
支持从 .env 文件或环境变量读取 API 密钥
"""
import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[str] = None) -> dict:
    """
    加载 .env 文件

    Args:
        env_path: .env 文件路径，如果为None则在当前目录和上级目录查找

    Returns:
        环境变量字典
    """
    if env_path:
        env_file = Path(env_path)
    else:
        # 尝试查找 .env 文件
        current_dir = Path.cwd()
        possible_paths = [
            current_dir / '.env',
            current_dir.parent / '.env',
            Path(__file__).parent / '.env',
        ]

        env_file = None
        for path in possible_paths:
            if path.exists():
                env_file = path
                break

    env_vars = {}

    if env_file and env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

    return env_vars


def get_api_key(key_name: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    获取 API 密钥（通用方法）

    优先级：
    1. 函数参数传入的 api_key
    2. 环境变量
    3. .env 文件

    Args:
        key_name: API密钥名称（如 CLAUDE_API_KEY）
        api_key: 直接传入的 API 密钥

    Returns:
        API 密钥，如果未找到则返回 None
    """
    # 1. 如果直接提供了密钥
    if api_key:
        return api_key

    # 2. 尝试从环境变量获取
    env_key = os.getenv(key_name)
    if env_key:
        return env_key

    # 3. 尝试从 .env 文件获取
    env_vars = load_env_file()
    if key_name in env_vars:
        return env_vars[key_name]

    return None


def get_claude_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """获取 Claude API 密钥（兼容旧版）"""
    return get_api_key('CLAUDE_API_KEY', api_key)


def get_openai_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """获取 OpenAI API 密钥（兼容旧版）"""
    return get_api_key('OPENAI_API_KEY', api_key)


def get_rate_limit(default: int = 4) -> int:
    """
    获取速率限制配置

    Args:
        default: 默认速率限制

    Returns:
        速率限制（每秒请求数）
    """
    # 从环境变量获取
    env_rate = os.getenv('RATE_LIMIT_PER_SECOND')
    if env_rate:
        try:
            return int(env_rate)
        except ValueError:
            pass

    # 从 .env 文件获取
    env_vars = load_env_file()
    if 'RATE_LIMIT_PER_SECOND' in env_vars:
        try:
            return int(env_vars['RATE_LIMIT_PER_SECOND'])
        except ValueError:
            pass

    return default


def print_api_key_status():
    """打印 API 密钥状态信息"""
    claude_key = get_claude_api_key()
    openai_key = get_openai_api_key()

    print("\n🔑 API密钥状态:")
    print("=" * 50)

    # Claude API
    if claude_key:
        masked_key = claude_key[:12] + '...' + claude_key[-4:] if len(claude_key) > 16 else '***'
        print(f"✅ Claude API: {masked_key}")
        if os.getenv('CLAUDE_API_KEY'):
            print(f"   来源: 环境变量 CLAUDE_API_KEY")
        else:
            env_vars = load_env_file()
            if 'CLAUDE_API_KEY' in env_vars:
                print(f"   来源: .env 文件")
    else:
        print("❌ Claude API: 未配置")

    # OpenAI API
    if openai_key:
        masked_key = openai_key[:7] + '...' + openai_key[-4:] if len(openai_key) > 11 else '***'
        print(f"✅ OpenAI API: {masked_key}")
        if os.getenv('OPENAI_API_KEY'):
            print(f"   来源: 环境变量 OPENAI_API_KEY")
        else:
            env_vars = load_env_file()
            if 'OPENAI_API_KEY' in env_vars:
                print(f"   来源: .env 文件")
    else:
        print("❌ OpenAI API: 未配置")

    print("=" * 50)

    # 如果都没配置，显示帮助
    if not claude_key and not openai_key:
        print("\n⚠️  请配置API密钥：")
        print("   1. 创建 .env 文件（参考 .env.example）")
        print("   2. 或设置环境变量:")
        print("      export CLAUDE_API_KEY=your-key")
        print("      export OPENAI_API_KEY=your-key")


if __name__ == "__main__":
    # 测试
    print_api_key_status()

    rate_limit = get_rate_limit()
    print(f"\n⚡ 速率限制: {rate_limit} 次/秒")
