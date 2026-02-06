"""
Embedding 客户端工厂
根据配置自动选择合适的 Embedding 客户端
"""
from typing import Optional, List
from ..config import Config


class EmbeddingClientBase:
    """Embedding客户端基类"""

    def embed(self, text: str) -> List[float]:
        """生成单个文本的向量"""
        raise NotImplementedError

    def embed_batch(self, texts: List[str], batch_size: int = 100, show_progress: bool = True) -> List[List[float]]:
        """批量生成文本向量"""
        raise NotImplementedError

    def get_embedding_dimension(self) -> int:
        """获取Embedding维度"""
        raise NotImplementedError


class OpenAIEmbeddingClient(EmbeddingClientBase):
    """OpenAI Embedding客户端"""

    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = Config.EMBEDDING_MODEL
        self.rate_limit = Config.RATE_LIMIT_PER_SECOND

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 100, show_progress: bool = True) -> List[List[float]]:
        import time

        if not texts:
            return []

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        if show_progress:
            print(f"\n🔄 批量生成Embedding (OpenAI): {len(texts)} 个文本，{total_batches} 个批次")
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

                if i + batch_size < len(texts):
                    time.sleep(1.0 / self.rate_limit)

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
        if "large" in self.model:
            return 3072
        else:
            return 1536


class ZhipuEmbeddingClient(EmbeddingClientBase):
    """智谱AI Embedding客户端"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from zhipuai import ZhipuAI
        except ImportError:
            raise ImportError("请先安装智谱AI SDK: pip install zhipuai")

        self.api_key = api_key or Config.ZHIPUAI_API_KEY
        if not self.api_key:
            raise ValueError("Zhipu AI API key is required")

        self.client = ZhipuAI(api_key=self.api_key)
        self.model = Config.ZHIPU_EMBEDDING_MODEL
        self.dimension = 1024

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str], batch_size: int = 10, show_progress: bool = True) -> List[List[float]]:
        import time

        if not texts:
            return []

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        if show_progress:
            print(f"\n🔄 批量生成Embedding (智谱AI): {len(texts)} 个文本，{total_batches} 个批次")
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

                if i + batch_size < len(texts):
                    time.sleep(0.2)  # 智谱AI速率限制

            except Exception as e:
                print(f"❌ 批次 {batch_num} 失败: {e}")
                all_embeddings.extend([[0.0] * self.dimension] * len(batch_texts))

        if show_progress:
            success_count = sum(1 for emb in all_embeddings if emb != [0.0] * len(emb))
            print("=" * 70)
            print(f"✅ 完成: {success_count}/{len(texts)} 成功")

        return all_embeddings

    def get_embedding_dimension(self) -> int:
        return self.dimension


def create_embedding_client(embedding_type: Optional[str] = None) -> EmbeddingClientBase:
    """
    创建Embedding客户端

    Args:
        embedding_type: 指定类型 ('openai', 'zhipu') 或 None（自动选择）

    Returns:
        Embedding客户端实例

    Raises:
        ValueError: 如果没有可用的配置
    """
    # 如果指定了类型
    if embedding_type:
        if embedding_type == "openai":
            print("📦 使用 OpenAI Embedding")
            return OpenAIEmbeddingClient()
        elif embedding_type == "zhipu":
            print("📦 使用 智谱AI Embedding")
            return ZhipuEmbeddingClient()
        else:
            raise ValueError(f"未知的Embedding类型: {embedding_type}")

    # 自动选择
    selected = Config.auto_select_embedding()

    if not selected:
        raise ValueError(
            "未配置任何Embedding API密钥\n"
            "请在 .env 文件中配置:\n"
            "  OPENAI_API_KEY=your-key  # OpenAI方案\n"
            "或\n"
            "  ZHIPUAI_API_KEY=your-key  # 智谱AI方案（推荐）"
        )

    if selected == "zhipu":
        print("📦 使用 智谱AI Embedding (自动选择)")
        return ZhipuEmbeddingClient()
    elif selected == "openai":
        print("📦 使用 OpenAI Embedding (自动选择)")
        return OpenAIEmbeddingClient()
    else:
        raise ValueError(f"未知的Embedding选择: {selected}")
