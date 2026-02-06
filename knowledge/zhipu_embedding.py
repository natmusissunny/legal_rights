"""
智谱AI Embedding客户端
兼容 OpenAI Embedding 接口的智谱AI适配器
"""
from typing import List, Union
from zhipuai import ZhipuAI


class ZhipuEmbedding:
    """智谱AI Embedding客户端（兼容OpenAI接口）"""

    def __init__(self, api_key: str, model: str = "embedding-2"):
        """
        初始化客户端

        Args:
            api_key: 智谱AI API密钥
            model: Embedding模型名称
                - embedding-2: 1024维（推荐）
                - embedding-3: 更高精度
        """
        self.client = ZhipuAI(api_key=api_key)
        self.model = model
        self.dimension = 1024 if model == "embedding-2" else 1024

    def embed(self, text: str) -> List[float]:
        """
        向量化单个文本（兼容OpenAI接口）

        Args:
            text: 输入文本

        Returns:
            向量列表（1024维）
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        批量向量化文本

        Args:
            texts: 文本列表
            batch_size: 批次大小

        Returns:
            向量列表
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

        return embeddings
