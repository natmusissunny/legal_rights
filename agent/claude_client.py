"""
Claude API 客户端
使用 Anthropic SDK 调用 Claude API
"""
from typing import Optional, List, Dict
from anthropic import Anthropic
import time

from ..config import Config


class ClaudeClient:
    """Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: Claude API密钥（如果为None则从Config读取）
        """
        self.api_key = api_key or Config.CLAUDE_API_KEY
        if not self.api_key:
            raise ValueError("Claude API key is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = Config.CLAUDE_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.rate_limit = Config.RATE_LIMIT_PER_SECOND
        self._last_request_time = 0

    def _wait_for_rate_limit(self):
        """等待速率限制"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)

        self._last_request_time = time.time()

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成回复

        Args:
            prompt: 用户提示
            system: 系统提示
            temperature: 温度参数（0-1）
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        self._wait_for_rate_limit()

        max_tokens = max_tokens or self.max_tokens

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Claude API 调用失败: {e}")
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
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成的文本
        """
        self._wait_for_rate_limit()

        max_tokens = max_tokens or self.max_tokens

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Claude API 调用失败: {e}")
            raise

    def stream_complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        流式生成回复

        Args:
            prompt: 用户提示
            system: 系统提示
            temperature: 温度参数
            max_tokens: 最大生成token数

        Yields:
            文本片段
        """
        self._wait_for_rate_limit()

        max_tokens = max_tokens or self.max_tokens

        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            print(f"❌ Claude API 调用失败: {e}")
            raise


def main():
    """测试函数"""
    import os

    # 检查API密钥
    if not Config.CLAUDE_API_KEY:
        print("❌ 请先配置 CLAUDE_API_KEY")
        print("   在 .env 文件中添加: CLAUDE_API_KEY=sk-ant-api03-...")
        return

    print("🧪 测试 Claude API 客户端")
    print("=" * 70)

    client = ClaudeClient()
    print(f"✅ 客户端初始化成功")
    print(f"   模型: {client.model}")
    print(f"   最大tokens: {client.max_tokens}")

    # 测试简单问答
    print("\n[测试1] 简单问答")
    print("-" * 70)

    prompt = "请用一句话解释什么是经济补偿金。"
    print(f"提问: {prompt}")
    print(f"\n回答: ", end="")

    try:
        response = client.complete(
            prompt=prompt,
            system="你是一位专业的劳动法律师，请用简洁专业的语言回答问题。",
            temperature=0.5
        )
        print(response)
    except Exception as e:
        print(f"失败: {e}")
        return

    # 测试多轮对话
    print("\n[测试2] 多轮对话")
    print("-" * 70)

    messages = [
        {"role": "user", "content": "我在公司工作了3年被辞退"},
        {"role": "assistant", "content": "我了解了。请问公司给出的辞退理由是什么？"},
        {"role": "user", "content": "说是业绩不好"}
    ]

    print("对话历史:")
    for msg in messages:
        role = "用户" if msg["role"] == "user" else "助手"
        print(f"  {role}: {msg['content']}")

    print(f"\n助手: ", end="")

    try:
        response = client.chat(
            messages=messages,
            system="你是一位专业的劳动法律师。",
            temperature=0.7
        )
        print(response)
    except Exception as e:
        print(f"失败: {e}")
        return

    # 测试流式输出
    print("\n[测试3] 流式输出")
    print("-" * 70)

    prompt = "请简要说明劳动仲裁的流程（3个步骤）"
    print(f"提问: {prompt}")
    print(f"\n回答: ", end="", flush=True)

    try:
        for chunk in client.stream_complete(
            prompt=prompt,
            system="你是一位专业的劳动法律师。",
            temperature=0.5
        ):
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"\n失败: {e}")
        return

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
