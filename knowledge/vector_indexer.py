"""
向量索引构建器
使用 FAISS 构建和管理向量索引
"""
import json
import pickle
from pathlib import Path
from typing import List, Optional
import numpy as np
import faiss

from ..models import Document, StructuredContent
from ..config import Config
from .embedding_client import EmbeddingClient
from .document_chunker import DocumentChunker


class VectorIndexer:
    """向量索引构建器"""

    def __init__(
        self,
        embedding_client: Optional[EmbeddingClient] = None,
        chunker: Optional[DocumentChunker] = None
    ):
        """
        初始化索引构建器

        Args:
            embedding_client: Embedding客户端
            chunker: 文档分块器
        """
        self.embedding_client = embedding_client or EmbeddingClient()
        self.chunker = chunker or DocumentChunker()
        self.index: Optional[faiss.Index] = None
        self.documents: List[Document] = []
        self.dimension = self.embedding_client.get_embedding_dimension()

    def build_index(
        self,
        contents: List[StructuredContent],
        show_progress: bool = True
    ):
        """
        构建向量索引

        Args:
            contents: 结构化内容列表
            show_progress: 是否显示进度
        """
        if show_progress:
            print("\n🏗️  构建向量索引")
            print("=" * 70)

        # 1. 分割文档
        if show_progress:
            print("\n[步骤1/3] 分割文档")
        self.documents = self.chunker.chunk_batch(contents, show_progress)

        if not self.documents:
            print("❌ 没有文档可以索引")
            return

        # 2. 生成向量
        if show_progress:
            print(f"\n[步骤2/3] 生成Embedding")

        texts = [doc.content for doc in self.documents]
        embeddings = self.embedding_client.embed_batch(
            texts,
            batch_size=100,
            show_progress=show_progress
        )

        # 将向量添加到文档
        for doc, embedding in zip(self.documents, embeddings):
            doc.embedding = embedding

        # 3. 构建FAISS索引
        if show_progress:
            print(f"\n[步骤3/3] 构建FAISS索引")
            print("-" * 70)

        # 转换为numpy数组
        vectors = np.array(embeddings, dtype=np.float32)

        # 创建FAISS索引（使用L2距离）
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors)

        if show_progress:
            print(f"✅ 索引构建完成")
            print(f"   文档数: {len(self.documents)}")
            print(f"   向量维度: {self.dimension}")
            print(f"   索引类型: IndexFlatL2")

    def save_index(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None
    ):
        """
        保存索引到文件

        Args:
            index_path: 索引文件路径
            metadata_path: 元数据文件路径
        """
        if self.index is None:
            raise ValueError("Index not built yet")

        # 默认路径
        if index_path is None:
            index_path = Config.VECTORS_DIR / "index.faiss"
        if metadata_path is None:
            metadata_path = Config.VECTORS_DIR / "metadata.pkl"

        print(f"\n💾 保存索引")
        print("-" * 70)

        # 保存FAISS索引
        faiss.write_index(self.index, str(index_path))
        print(f"✅ FAISS索引已保存: {index_path}")

        # 保存元数据（文档列表）
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.documents, f)
        print(f"✅ 元数据已保存: {metadata_path}")

        # 保存统计信息（JSON格式，便于查看）
        stats_path = Config.VECTORS_DIR / "stats.json"
        stats = {
            "total_documents": len(self.documents),
            "vector_dimension": self.dimension,
            "index_type": "IndexFlatL2",
            "sources": list(set(doc.source_url for doc in self.documents)),
            "sections": list(set(doc.section_title for doc in self.documents if doc.section_title))
        }

        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"✅ 统计信息已保存: {stats_path}")

    def load_index(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None
    ):
        """
        从文件加载索引

        Args:
            index_path: 索引文件路径
            metadata_path: 元数据文件路径
        """
        # 默认路径
        if index_path is None:
            index_path = Config.VECTORS_DIR / "index.faiss"
        if metadata_path is None:
            metadata_path = Config.VECTORS_DIR / "metadata.pkl"

        print(f"\n📂 加载索引")
        print("-" * 70)

        # 加载FAISS索引
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        self.index = faiss.read_index(str(index_path))
        print(f"✅ FAISS索引已加载: {index_path}")

        # 加载元数据
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        with open(metadata_path, 'rb') as f:
            self.documents = pickle.load(f)
        print(f"✅ 元数据已加载: {metadata_path}")

        print(f"   文档数: {len(self.documents)}")
        print(f"   向量维度: {self.index.d}")

    def search(
        self,
        query: str,
        top_k: int = None
    ) -> List[tuple[Document, float]]:
        """
        搜索相似文档

        Args:
            query: 查询文本
            top_k: 返回Top-K结果

        Returns:
            (文档, 距离) 列表
        """
        if self.index is None:
            raise ValueError("Index not loaded")

        top_k = top_k or Config.TOP_K_RESULTS

        # 生成查询向量
        query_embedding = self.embedding_client.embed(query)
        query_vector = np.array([query_embedding], dtype=np.float32)

        # 搜索
        distances, indices = self.index.search(query_vector, top_k)

        # 返回结果
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                # 将L2距离转换为相似度分数（距离越小，相似度越高）
                # 使用 1 / (1 + distance) 将距离映射到 (0, 1]
                similarity = 1.0 / (1.0 + float(distance))
                results.append((doc, similarity))

        return results

    def get_stats(self) -> dict:
        """
        获取索引统计信息

        Returns:
            统计信息字典
        """
        if self.index is None or not self.documents:
            return {
                "indexed": False,
                "total_documents": 0
            }

        return {
            "indexed": True,
            "total_documents": len(self.documents),
            "vector_dimension": self.dimension,
            "sources": list(set(doc.source_url for doc in self.documents)),
            "sections": list(set(doc.section_title for doc in self.documents if doc.section_title))
        }


def main():
    """测试函数"""
    from ..scraper import HTMLCleaner, ContentParser

    print("🧪 测试向量索引构建器")
    print("=" * 70)

    # 检查API密钥
    if not Config.OPENAI_API_KEY:
        print("❌ 请先配置 OPENAI_API_KEY")
        return

    # 读取示例HTML
    sample_html_path = Config.PROJECT_ROOT / "data" / "cache" / "sample_legal_content.html"
    if not sample_html_path.exists():
        print(f"❌ 示例文件不存在: {sample_html_path}")
        return

    html = sample_html_path.read_text(encoding='utf-8')

    # 解析内容
    cleaner = HTMLCleaner()
    parser = ContentParser()

    cleaned_html, _ = cleaner.clean_and_extract(html)
    structured = parser.parse(
        html=cleaned_html,
        url="https://example.com/sample",
        title="离职经济补偿指南"
    )

    # 构建索引
    indexer = VectorIndexer()
    indexer.build_index([structured], show_progress=True)

    # 保存索引
    indexer.save_index()

    # 测试搜索
    print("\n🔍 测试搜索")
    print("=" * 70)

    queries = [
        "如何计算经济补偿金？",
        "N+1补偿是什么意思？",
        "劳动仲裁需要什么材料？"
    ]

    for query in queries:
        print(f"\n查询: {query}")
        print("-" * 70)

        results = indexer.search(query, top_k=3)

        for i, (doc, score) in enumerate(results, 1):
            print(f"\n结果 {i} (相似度: {score:.4f})")
            print(f"章节: {doc.section_title}")
            print(f"内容: {doc.content[:100]}...")

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
