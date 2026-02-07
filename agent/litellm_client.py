"""
LiteLLM 客户端
通过 LiteLLM 统一调用各种大模型
"""
from typing import Optional, List, Dict
from ..config import Config


class LiteLLMClient:
    """LiteLLM 统一客户端"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        初始化 LiteLLM 客户端

        Args:
            model: 模型名称（如 'gpt-4', 'claude-3-opus'）
            api_base: LiteLLM 代理地址（如 'http://localhost:4000'）
            api_key: LiteLLM API密钥（如果需要）

        Examples:
            # 方式1: 使用 LiteLLM 代理
            client = LiteLLMClient(
                model="gpt-4",
                api_base="http://localhost:4000"
            )

            # 方式2: 直接使用 LiteLLM
            client = LiteLLMClient(model="claude-3-opus")
        """
        try:
            from litellm import completion
        except ImportError:
            raise ImportError(
                "请先安装 LiteLLM: pip install litellm\n"
                "文档: https://docs.litellm.ai/"
            )

        self.completion = completion
        self.model = model or Config.LITELLM_MODEL
        self.api_base = api_base or Config.LITELLM_API_BASE
        self.api_key = api_key or Config.LITELLM_API_KEY
        self.max_tokens = Config.MAX_TOKENS

        if not self.model:
            raise ValueError(
                "未配置 LiteLLM 模型\n"
                "请在 .env 中设置:\n"
                "  LITELLM_MODEL=gpt-4  # 或其他模型\n"
                "支持的模型: https://docs.litellm.ai/docs/providers"
            )

        print(f"📦 使用 LiteLLM 统一接口")
        print(f"   模型: {self.model}")
        if self.api_base:
            print(f"   代理: {self.api_base}")

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成单次回复

        Args:
            prompt: 用户提示
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        max_tokens = max_tokens or self.max_tokens

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # 构建参数
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # 如果配置了代理地址
        if self.api_base:
            kwargs["api_base"] = self.api_base

        # 如果配置了API密钥
        if self.api_key:
            kwargs["api_key"] = self.api_key

        try:
            response = self.completion(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ LiteLLM 调用失败: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        多轮对话

        Args:
            messages: 消息列表
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        max_tokens = max_tokens or self.max_tokens

        # 如果有system，插入到开头
        if system:
            messages = [{"role": "system", "content": system}] + messages

        # 构建参数
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if self.api_base:
            kwargs["api_base"] = self.api_base

        if self.api_key:
            kwargs["api_key"] = self.api_key

        try:
            response = self.completion(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ LiteLLM 调用失败: {e}")
            raise


def test_litellm():
    """测试 LiteLLM 配置"""
    print("🧪 测试 LiteLLM 配置")
    print("=" * 70)

    try:
        client = LiteLLMClient()

        print("\n测试单次对话...")
        response = client.complete(
            prompt="用一句话解释什么是劳动合同。",
            system="你是劳动法律师。",
            temperature=0.5,
            max_tokens=100
        )

        print(f"✅ 成功")
        print(f"回答: {response}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_litellm()
