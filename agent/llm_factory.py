"""
LLM 客户端工厂
根据配置自动选择合适的 LLM 客户端
支持: Claude, 通义千问, DeepSeek, 智谱AI(GLM), 元宝(MiniMax), Kimi
"""
from typing import Optional, List, Dict
from ..config import Config


class LLMClientBase:
    """LLM客户端基类"""

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """生成单次回复"""
        raise NotImplementedError

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """多轮对话"""
        raise NotImplementedError


class ClaudeClient(LLMClientBase):
    """Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        from anthropic import Anthropic
        self.api_key = api_key or Config.CLAUDE_API_KEY
        if not self.api_key:
            raise ValueError("Claude API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = Config.CLAUDE_MODEL
        self.max_tokens = Config.MAX_TOKENS

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=messages
        )

        return response.content[0].text


class QwenClient(LLMClientBase):
    """通义千问 API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from dashscope import Generation
        except ImportError:
            raise ImportError("请先安装通义千问SDK: pip install dashscope")

        self.api_key = api_key or Config.DASHSCOPE_API_KEY
        if not self.api_key:
            raise ValueError("Dashscope API key is required")

        self.Generation = Generation
        self.model = Config.QWEN_MODEL
        self.max_tokens = Config.MAX_TOKENS

        # 设置API密钥
        import dashscope
        dashscope.api_key = self.api_key

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.Generation.call(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format='message'
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"通义千问API调用失败: {response.message}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        # 如果有system，插入到开头
        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self.Generation.call(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format='message'
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"通义千问API调用失败: {response.message}")


class DeepSeekClient(LLMClientBase):
    """DeepSeek API 客户端（兼容OpenAI接口）"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请先安装OpenAI SDK: pip install openai")

        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = Config.DEEPSEEK_MODEL
        self.max_tokens = Config.MAX_TOKENS

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


class ZhipuClient(LLMClientBase):
    """智谱AI (GLM) API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from zhipuai import ZhipuAI
        except ImportError:
            raise ImportError("请先安装智谱AI SDK: pip install zhipuai")

        self.api_key = api_key or Config.ZHIPUAI_API_KEY
        if not self.api_key:
            raise ValueError("Zhipu AI API key is required")

        self.client = ZhipuAI(api_key=self.api_key)
        self.model = Config.ZHIPU_CHAT_MODEL
        self.max_tokens = Config.MAX_TOKENS

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


class MinimaxClient(LLMClientBase):
    """元宝 (MiniMax) API 客户端"""

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        try:
            import requests
        except ImportError:
            raise ImportError("请先安装 requests: pip install requests")

        self.api_key = api_key or Config.MINIMAX_API_KEY
        self.group_id = group_id or Config.MINIMAX_GROUP_ID
        if not self.api_key or not self.group_id:
            raise ValueError("MiniMax API key and group_id are required")

        self.requests = requests
        self.model = Config.MINIMAX_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.base_url = f"https://api.minimax.chat/v1/text/chatcompletion_v2?GroupId={self.group_id}"

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = self.requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        if system:
            messages = [{"role": "system", "content": system}] + messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = self.requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]


class KimiClient(LLMClientBase):
    """Kimi (月之暗面) API 客户端（兼容OpenAI接口）"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请先安装OpenAI SDK: pip install openai")

        self.api_key = api_key or Config.KIMI_API_KEY
        if not self.api_key:
            raise ValueError("Kimi API key is required")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        self.model = Config.KIMI_MODEL
        self.max_tokens = Config.MAX_TOKENS

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        max_tokens = max_tokens or self.max_tokens

        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


def create_llm_client(llm_type: Optional[str] = None) -> LLMClientBase:
    """
    创建LLM客户端

    Args:
        llm_type: 指定类型 ('claude', 'qwen', 'deepseek', 'zhipu', 'minimax', 'kimi') 或 None（自动选择）

    Returns:
        LLM客户端实例

    Raises:
        ValueError: 如果没有可用的配置
    """
    # 如果指定了类型
    if llm_type:
        client_map = {
            "claude": ClaudeClient,
            "qwen": QwenClient,
            "deepseek": DeepSeekClient,
            "zhipu": ZhipuClient,
            "minimax": MinimaxClient,
            "kimi": KimiClient,
        }

        if llm_type not in client_map:
            raise ValueError(f"未知的LLM类型: {llm_type}")

        print(f"📦 使用 {llm_type.upper()} LLM")
        return client_map[llm_type]()

    # 自动选择
    selected = Config.auto_select_llm()

    if not selected:
        raise ValueError(
            "未配置任何LLM API密钥\n"
            "请在 .env 文件中配置以下任一项:\n"
            "  DASHSCOPE_API_KEY=your-key     # 通义千问（推荐，国内）\n"
            "  DEEPSEEK_API_KEY=your-key      # DeepSeek（推荐，便宜）\n"
            "  ZHIPUAI_API_KEY=your-key       # 智谱AI GLM（国内）\n"
            "  KIMI_API_KEY=your-key          # Kimi 月之暗面（国内）\n"
            "  MINIMAX_API_KEY=your-key       # 元宝 MiniMax（国内）\n"
            "  CLAUDE_API_KEY=your-key        # Claude（国际，需代理）"
        )

    client_map = {
        "qwen": (QwenClient, "通义千问 Qwen"),
        "deepseek": (DeepSeekClient, "DeepSeek"),
        "zhipu": (ZhipuClient, "智谱AI GLM"),
        "kimi": (KimiClient, "Kimi 月之暗面"),
        "minimax": (MinimaxClient, "元宝 MiniMax"),
        "claude": (ClaudeClient, "Claude"),
    }

    if selected in client_map:
        client_class, display_name = client_map[selected]
        print(f"📦 使用 {display_name} (自动选择)")
        return client_class()
    else:
        raise ValueError(f"未知的LLM选择: {selected}")
