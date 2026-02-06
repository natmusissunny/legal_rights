"""
Embedding API 客户端
使用 OpenAI Embedding API 生成文本向量
"""
import asyncio
import time
from typing import List, Optional
from openai import OpenAI
import numpy as np

from ..config import Config


class EmbeddingClient:
    """Embedding API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: OpenAI API密钥（如果为None则从Config读取）
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = Config.EMBEDDING_MODEL
        self.rate_limit = Config.RATE_LIMIT_PER_SECOND
        self._last_request_time = 0

    async def _wait_for_rate_limit(self):
        """等待速率限制"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self._last_request_time = time.time()

    def embed(self, text: str) -> List[float]:
        """
        生成单个文本的向量

        Args:
            text: 输入文本

        Returns:
            向量（浮点数列表）
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding生成失败: {e}")
            raise

    async def embed_async(self, text: str) -> List[float]:
        """
        异步生成单个文本的向量

        Args:
            text: 输入文本

        Returns:
            向量（浮点数列表）
        """
        await self._wait_for_rate_limit()
        return self.embed(text)

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        批量生成文本向量

        Args:
            texts: 文本列表
            batch_size: 批次大小（OpenAI API最大2048）
            show_progress: 是否显示进度

        Returns:
            向量列表
        """
        if not texts:
            return []

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        if show_progress:
            print(f"\n🔄 批量生成Embedding: {len(texts)} 个文本，{total_batches} 个批次")
            print("=" * 70)

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                if show_progress:
                    print(f"[批次 {batch_num}/{total_batches}] 处理 {len(batch_texts)} 个文本...", end=" ")

                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts
                )

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                if show_progress:
                    print(f"✅ 完成")

                # 速率限制
                if i + batch_size < len(texts):
                    time.sleep(1.0 / self.rate_limit)

            except Exception as e:
                print(f"❌ 批次 {batch_num} 失败: {e}")
                # 失败时添加零向量
                embedding_dim = 1536  # text-embedding-3-small 的维度
                all_embeddings.extend([[0.0] * embedding_dim] * len(batch_texts))

        if show_progress:
            success_count = sum(1 for emb in all_embeddings if emb != [0.0] * len(emb))
            print("=" * 70)
            print(f"✅ 完成: {success_count}/{len(texts)} 成功")

        return all_embeddings

    async def embed_batch_async(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        异步批量生成文本向量

        Args:
            texts: 文本列表
            batch_size: 批次大小
            show_progress: 是否显示进度

        Returns:
            向量列表
        """
        if not texts:
            return []

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        if show_progress:
            print(f"\n🔄 异步批量生成Embedding: {len(texts)} 个文本，{total_batches} 个批次")
            print("=" * 70)

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            await self._wait_for_rate_limit()

            try:
                if show_progress:
                    print(f"[批次 {batch_num}/{total_batches}] 处理 {len(batch_texts)} 个文本...", end=" ")

                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts
                )

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

                if show_progress:
                    print(f"✅ 完成")

            except Exception as e:
                print(f"❌ 批次 {batch_num} 失败: {e}")
                embedding_dim = 1536
                all_embeddings.extend([[0.0] * embedding_dim] * len(batch_texts))

        if show_progress:
            success_count = sum(1 for emb in all_embeddings if emb != [0.0] * len(emb))
            print("=" * 70)
            print(f"✅ 完成: {success_count}/{len(texts)} 成功")

        return all_embeddings

    def get_embedding_dimension(self) -> int:
        """
        获取Embedding维度

        Returns:
            向量维度
        """
        # text-embedding-3-small: 1536维
        # text-embedding-3-large: 3072维
        if "large" in self.model:
            return 3072
        else:
            return 1536

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            相似度（0-1）
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # 计算余弦相似度
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


def main():
    """测试函数"""
    import os

    # 检查API密钥
    if not Config.OPENAI_API_KEY:
        print("❌ 请先配置 OPENAI_API_KEY")
        print("   在 .env 文件中添加: OPENAI_API_KEY=your-key")
        return

    print("🧪 测试 Embedding 客户端")
    print("=" * 70)

    client = EmbeddingClient()

    # 测试单个文本
    print("\n[测试1] 单个文本Embedding")
    print("-" * 70)
    text = "公司恶意辞退员工应该如何维权？"
    print(f"文本: {text}")

    try:
        embedding = client.embed(text)
        print(f"✅ Embedding生成成功")
        print(f"   维度: {len(embedding)}")
        print(f"   前10维: {embedding[:10]}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return

    # 测试批量生成
    print("\n[测试2] 批量Embedding")
    print("-" * 70)
    texts = [
        "N+1补偿金如何计算？",
        "劳动仲裁需要准备什么材料？",
        "试用期被辞退有补偿吗？",
        "工作年限怎么算？",
        "月平均工资包括哪些？"
    ]

    embeddings = client.embed_batch(texts, batch_size=5)
    print(f"\n生成了 {len(embeddings)} 个向量")

    # 测试相似度计算
    print("\n[测试3] 相似度计算")
    print("-" * 70)
    query = "如何计算经济补偿金？"
    query_embedding = client.embed(query)

    print(f"查询: {query}")
    print(f"\n与各文本的相似度:")
    for i, text in enumerate(texts):
        similarity = client.cosine_similarity(query_embedding, embeddings[i])
        print(f"  {i+1}. {text}")
        print(f"     相似度: {similarity:.4f}")

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
