"""
测试向量索引完整流程
从文档分块到索引构建再到知识检索
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.scraper import HTMLCleaner, ContentParser
from legal_rights.knowledge import (
    EmbeddingClient,
    DocumentChunker,
    VectorIndexer,
    KnowledgeRetriever
)
from legal_rights.config import Config


def test_embedding_client():
    """测试Embedding客户端"""
    print("🧪 [测试1] Embedding客户端")
    print("=" * 80)

    try:
        client = EmbeddingClient()
        print("✅ 客户端初始化成功")
        print(f"   模型: {client.model}")
        print(f"   维度: {client.get_embedding_dimension()}")

        # 测试单个文本
        text = "公司恶意辞退员工应该如何维权？"
        embedding = client.embed(text)
        print(f"\n✅ 测试Embedding生成成功")
        print(f"   文本: {text}")
        print(f"   向量维度: {len(embedding)}")
        print(f"   向量前5维: {embedding[:5]}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_document_chunker():
    """测试文档分块"""
    print("\n\n🧪 [测试2] 文档分块")
    print("=" * 80)

    # 读取示例HTML
    sample_html_path = project_root / "data" / "cache" / "sample_legal_content.html"
    if not sample_html_path.exists():
        print(f"❌ 示例文件不存在: {sample_html_path}")
        return False

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

    print(f"✅ 文档解析完成")
    print(f"   标题: {structured.title}")
    print(f"   章节数: {len(structured.sections)}")

    # 分块
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)
    documents = chunker.chunk_structured_content(structured)

    print(f"\n✅ 文档分块完成")
    print(f"   总块数: {len(documents)}")
    print(f"\n前3个文档块:")
    for i, doc in enumerate(documents[:3], 1):
        print(f"\n  块 {i}:")
        print(f"    ID: {doc.id}")
        print(f"    章节: {doc.section_title}")
        print(f"    长度: {len(doc.content)} 字符")
        print(f"    内容预览: {doc.content[:100]}...")

    return structured, documents


def test_vector_indexer(structured):
    """测试向量索引构建"""
    print("\n\n🧪 [测试3] 向量索引构建")
    print("=" * 80)

    try:
        indexer = VectorIndexer()
        indexer.build_index([structured], show_progress=True)

        print(f"\n✅ 索引构建完成")
        stats = indexer.get_stats()
        print(f"   文档数: {stats['total_documents']}")
        print(f"   向量维度: {stats['vector_dimension']}")

        # 保存索引
        indexer.save_index()

        return indexer
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_knowledge_retriever():
    """测试知识检索"""
    print("\n\n🧪 [测试4] 知识检索")
    print("=" * 80)

    try:
        retriever = KnowledgeRetriever(auto_load=True)

        queries = [
            "如何计算N+1经济补偿金？",
            "劳动仲裁需要什么材料？",
            "试用期被辞退有补偿吗？"
        ]

        for query in queries:
            print(f"\n查询: {query}")
            print("-" * 70)

            results = retriever.retrieve(query, top_k=3)

            for i, (doc, score) in enumerate(results, 1):
                print(f"\n  结果 {i} (相似度: {score:.4f})")
                print(f"    章节: {doc.section_title}")
                print(f"    内容: {doc.content[:120]}...")

        print(f"\n✅ 检索测试完成")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 向量索引模块完整测试")
    print("=" * 80)
    print()

    # 检查API密钥
    if not Config.OPENAI_API_KEY:
        print("❌ 错误: 未配置 OPENAI_API_KEY")
        print("   请在 .env 文件中添加: OPENAI_API_KEY=your-key")
        return

    results = {
        "embedding": False,
        "chunker": False,
        "indexer": False,
        "retriever": False
    }

    # 测试1: Embedding客户端
    results["embedding"] = test_embedding_client()

    if not results["embedding"]:
        print("\n❌ Embedding测试失败，终止测试")
        return

    # 测试2: 文档分块
    test_result = test_document_chunker()
    if test_result:
        structured, documents = test_result
        results["chunker"] = True
    else:
        print("\n❌ 文档分块测试失败，终止测试")
        return

    # 测试3: 向量索引构建
    indexer = test_vector_indexer(structured)
    results["indexer"] = indexer is not None

    if not results["indexer"]:
        print("\n❌ 索引构建测试失败，终止测试")
        return

    # 测试4: 知识检索
    results["retriever"] = test_knowledge_retriever()

    # 总结
    print("\n\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)

    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name:15s}: {status}")

    all_pass = all(results.values())
    print("\n" + "=" * 80)
    if all_pass:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败")
    print("=" * 80)


if __name__ == "__main__":
    main()
