"""
知识检索器
提供高级检索功能，包括重排序和结果过滤
"""
from typing import List, Optional
from pathlib import Path

from ..models import Document
from ..config import Config
from .vector_indexer import VectorIndexer
from .embedding_factory import create_embedding_client, EmbeddingClientBase


class KnowledgeRetriever:
    """知识检索器"""

    def __init__(
        self,
        indexer: Optional[VectorIndexer] = None,
        auto_load: bool = True
    ):
        """
        初始化检索器

        Args:
            indexer: 向量索引器
            auto_load: 是否自动加载索引
        """
        if indexer is None:
            indexer = VectorIndexer()
            if auto_load:
                try:
                    indexer.load_index()
                except FileNotFoundError:
                    print("⚠️  索引文件不存在，请先构建索引")

        self.indexer = indexer

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        min_score: float = 0.0,
        filter_section: Optional[str] = None
    ) -> List[tuple[Document, float]]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回Top-K结果
            min_score: 最小相似度阈值
            filter_section: 过滤特定章节

        Returns:
            (文档, 相似度) 列表
        """
        top_k = top_k or Config.TOP_K_RESULTS

        # 向量检索
        results = self.indexer.search(query, top_k=top_k * 2)  # 多检索一些用于过滤

        # 过滤结果
        filtered_results = []
        for doc, score in results:
            # 分数过滤
            if score < min_score:
                continue

            # 章节过滤
            if filter_section and doc.section_title != filter_section:
                continue

            filtered_results.append((doc, score))

        # 限制返回数量
        return filtered_results[:top_k]

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = None
    ) -> str:
        """
        检索并组合为上下文文本

        Args:
            query: 查询文本
            top_k: 返回Top-K结果

        Returns:
            组合的上下文文本
        """
        results = self.retrieve(query, top_k=top_k)

        if not results:
            return ""

        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            section_info = f"[{doc.section_title}]" if doc.section_title else ""
            context_parts.append(
                f"### 参考文档 {i} {section_info} (相关度: {score:.2f})\n"
                f"{doc.content}\n"
            )

        return "\n".join(context_parts)

    def retrieve_by_keyword(
        self,
        keywords: List[str],
        top_k: int = None
    ) -> List[Document]:
        """
        关键词检索（简单的文本匹配）

        Args:
            keywords: 关键词列表
            top_k: 返回Top-K结果

        Returns:
            文档列表
        """
        if not self.indexer.documents:
            return []

        top_k = top_k or Config.TOP_K_RESULTS

        # 计算每个文档的关键词匹配分数
        doc_scores = []
        for doc in self.indexer.documents:
            content_lower = doc.content.lower()
            score = sum(1 for kw in keywords if kw.lower() in content_lower)

            if score > 0:
                doc_scores.append((doc, score))

        # 按分数排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        # 返回Top-K
        return [doc for doc, _ in doc_scores[:top_k]]

    def hybrid_retrieve(
        self,
        query: str,
        keywords: Optional[List[str]] = None,
        top_k: int = None,
        vector_weight: float = 0.7
    ) -> List[tuple[Document, float]]:
        """
        混合检索（向量 + 关键词）

        Args:
            query: 查询文本
            keywords: 关键词列表
            top_k: 返回Top-K结果
            vector_weight: 向量检索的权重（0-1）

        Returns:
            (文档, 综合分数) 列表
        """
        top_k = top_k or Config.TOP_K_RESULTS
        keyword_weight = 1.0 - vector_weight

        # 向量检索
        vector_results = self.retrieve(query, top_k=top_k * 2)
        vector_scores = {doc.id: score for doc, score in vector_results}

        # 关键词检索
        keyword_scores = {}
        if keywords:
            keyword_results = self.retrieve_by_keyword(keywords, top_k=top_k * 2)
            max_kw_score = len(keywords)
            for doc in keyword_results:
                content_lower = doc.content.lower()
                score = sum(1 for kw in keywords if kw.lower() in content_lower)
                # 归一化到 0-1
                keyword_scores[doc.id] = score / max_kw_score if max_kw_score > 0 else 0

        # 合并分数
        all_doc_ids = set(vector_scores.keys()) | set(keyword_scores.keys())
        combined_results = []

        for doc_id in all_doc_ids:
            v_score = vector_scores.get(doc_id, 0.0)
            k_score = keyword_scores.get(doc_id, 0.0)

            # 计算综合分数
            combined_score = vector_weight * v_score + keyword_weight * k_score

            # 找到对应的文档
            doc = None
            for d in self.indexer.documents:
                if d.id == doc_id:
                    doc = d
                    break

            if doc:
                combined_results.append((doc, combined_score))

        # 按综合分数排序
        combined_results.sort(key=lambda x: x[1], reverse=True)

        return combined_results[:top_k]

    def get_stats(self) -> dict:
        """
        获取检索器统计信息

        Returns:
            统计信息字典
        """
        return self.indexer.get_stats()


def main():
    """测试函数"""
    print("🧪 测试知识检索器")
    print("=" * 70)

    # 检查索引是否存在
    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("❌ 索引不存在，请先运行 vector_indexer.py 构建索引")
        return

    # 初始化检索器
    retriever = KnowledgeRetriever(auto_load=True)

    # 测试向量检索
    print("\n[测试1] 向量检索")
    print("-" * 70)

    query = "如何计算N+1经济补偿金？"
    print(f"查询: {query}\n")

    results = retriever.retrieve(query, top_k=3)

    for i, (doc, score) in enumerate(results, 1):
        print(f"结果 {i} (相似度: {score:.4f})")
        print(f"章节: {doc.section_title}")
        print(f"内容: {doc.content[:150]}...")
        print()

    # 测试上下文生成
    print("\n[测试2] 上下文生成")
    print("-" * 70)

    context = retriever.retrieve_with_context(query, top_k=2)
    print(context[:500] + "...\n")

    # 测试关键词检索
    print("\n[测试3] 关键词检索")
    print("-" * 70)

    keywords = ["N+1", "补偿金", "代通知金"]
    print(f"关键词: {keywords}\n")

    kw_results = retriever.retrieve_by_keyword(keywords, top_k=3)

    for i, doc in enumerate(kw_results, 1):
        print(f"结果 {i}")
        print(f"章节: {doc.section_title}")
        print(f"内容: {doc.content[:150]}...")
        print()

    # 测试混合检索
    print("\n[测试4] 混合检索")
    print("-" * 70)

    hybrid_results = retriever.hybrid_retrieve(
        query="经济补偿",
        keywords=["补偿", "工资"],
        top_k=3
    )

    for i, (doc, score) in enumerate(hybrid_results, 1):
        print(f"结果 {i} (综合分数: {score:.4f})")
        print(f"章节: {doc.section_title}")
        print(f"内容: {doc.content[:150]}...")
        print()

    print("=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
