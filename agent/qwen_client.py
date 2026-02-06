"""
通义千问客户端
兼容 Claude API 接口的通义千问适配器
"""
from typing import Optional
import dashscope
from dashscope import Generation


class QwenClient:
    """通义千问客户端（兼容Claude接口）"""

    def __init__(self, api_key: str, model: str = "qwen-max"):
        """
        初始化客户端

        Args:
            api_key: 通义千问API密钥
            model: 模型名称
                - qwen-max: 最强性能（推荐）
                - qwen-plus: 平衡性能
                - qwen-turbo: 最快速度
        """
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        生成回答（兼容Claude接口）

        Args:
            prompt: 用户提示词
            system: 系统角色定义
            temperature: 温度参数（0-2）
            max_tokens: 最大生成token数

        Returns:
            生成的回答文本
        """
        # 构建消息列表
        messages = []

        # 添加系统消息
        if system:
            messages.append({
                'role': 'system',
                'content': system
            })

        # 添加用户消息
        messages.append({
            'role': 'user',
            'content': prompt
        })

        # 调用通义千问API
        response = Generation.call(
            model=self.model,
            messages=messages,
            result_format='message',
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.8
        )

        # 检查响应
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"通义千问API调用失败: {response.code} - {response.message}")

    def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        流式生成回答

        Args:
            prompt: 用户提示词
            system: 系统角色定义
            temperature: 温度参数
            max_tokens: 最大生成token数

        Yields:
            生成的文本片段
        """
        messages = []

        if system:
            messages.append({'role': 'system', 'content': system})

        messages.append({'role': 'user', 'content': prompt})

        # 流式调用
        responses = Generation.call(
            model=self.model,
            messages=messages,
            result_format='message',
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            incremental_output=True
        )

        for response in responses:
            if response.status_code == 200:
                yield response.output.choices[0].message.content
            else:
                raise Exception(f"通义千问API调用失败: {response.code}")
