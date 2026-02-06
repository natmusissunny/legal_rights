"""
文档分块器
将长文本分割成小块以便于向量检索
"""
from typing import List
import re

from ..models import Document, StructuredContent, LegalSection
from ..config import Config


class DocumentChunker:
    """文档分块器"""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        初始化分块器

        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 重叠大小（字符数）
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    def chunk_text(
        self,
        text: str,
        metadata: dict = None
    ) -> List[str]:
        """
        分割文本

        Args:
            text: 输入文本
            metadata: 元数据

        Returns:
            文本块列表
        """
        if not text or not text.strip():
            return []

        # 清理文本
        text = text.strip()

        # 如果文本短于chunk_size，直接返回
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # 计算结束位置
            end = start + self.chunk_size

            # 如果不是最后一块，尝试在句子边界分割
            if end < len(text):
                # 查找句子结束符
                sentence_ends = ['.', '。', '!', '！', '?', '？', '\n']
                best_end = end

                # 在 chunk_size 附近查找句子边界
                search_start = max(start + self.chunk_size // 2, start)
                search_end = min(end + 50, len(text))

                for i in range(end, search_start, -1):
                    if i < len(text) and text[i] in sentence_ends:
                        best_end = i + 1
                        break

                end = best_end

            # 提取块
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 下一块的开始位置（考虑重叠）
            start = end - self.chunk_overlap

            # 避免无限循环
            if start <= end - self.chunk_size + self.chunk_overlap:
                start = end

        return chunks

    def chunk_section(
        self,
        section: LegalSection,
        source_url: str,
        base_id: str = ""
    ) -> List[Document]:
        """
        分割章节为文档块

        Args:
            section: 法律章节
            source_url: 来源URL
            base_id: 基础ID

        Returns:
            文档块列表
        """
        documents = []

        # 生成当前章节的ID
        section_id = f"{base_id}/{section.title}" if base_id else section.title

        # 分割当前章节的内容
        if section.content:
            chunks = self.chunk_text(section.content)

            for i, chunk in enumerate(chunks):
                doc = Document(
                    id=f"{section_id}#chunk{i}",
                    content=chunk,
                    source_url=source_url,
                    section_title=section.title,
                    metadata={
                        "level": section.level,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)

        # 递归处理子章节
        for subsection in section.subsections:
            sub_documents = self.chunk_section(subsection, source_url, section_id)
            documents.extend(sub_documents)

        return documents

    def chunk_structured_content(
        self,
        content: StructuredContent
    ) -> List[Document]:
        """
        分割结构化内容为文档块

        Args:
            content: 结构化内容

        Returns:
            文档块列表
        """
        documents = []

        # 添加标题作为第一个文档
        if content.title:
            title_doc = Document(
                id=f"{content.url}#title",
                content=content.title,
                source_url=content.url,
                section_title="标题",
                metadata={
                    "level": 0,
                    "is_title": True,
                    "scraped_at": content.scraped_at.isoformat()
                }
            )
            documents.append(title_doc)

        # 处理所有章节
        for section in content.sections:
            section_documents = self.chunk_section(section, content.url)
            documents.extend(section_documents)

        return documents

    def chunk_batch(
        self,
        contents: List[StructuredContent],
        show_progress: bool = True
    ) -> List[Document]:
        """
        批量分割文档

        Args:
            contents: 结构化内容列表
            show_progress: 是否显示进度

        Returns:
            所有文档块
        """
        all_documents = []

        if show_progress:
            print(f"\n📝 分割文档: {len(contents)} 个文档")
            print("=" * 70)

        for i, content in enumerate(contents, 1):
            if show_progress:
                print(f"[{i}/{len(contents)}] {content.title}...", end=" ")

            documents = self.chunk_structured_content(content)
            all_documents.extend(documents)

            if show_progress:
                print(f"✅ {len(documents)} 块")

        if show_progress:
            print("=" * 70)
            print(f"✅ 完成: 总共 {len(all_documents)} 个文档块")

        return all_documents


def main():
    """测试函数"""
    print("🧪 测试文档分块器")
    print("=" * 70)

    chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)

    # 测试简单文本分割
    print("\n[测试1] 简单文本分割")
    print("-" * 70)

    text = """根据《中华人民共和国劳动合同法》第46条、第47条的规定，用人单位在以下情形下应当向劳动者支付经济补偿。
经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。
如果用人单位未提前30日以书面形式通知劳动者解除劳动合同，应额外支付劳动者一个月工资。这就是常说的"N+1"补偿。"""

    print(f"原文 ({len(text)} 字符):")
    print(text[:100] + "...")

    chunks = chunker.chunk_text(text)
    print(f"\n分割结果: {len(chunks)} 块")
    for i, chunk in enumerate(chunks):
        print(f"\n块 {i+1} ({len(chunk)} 字符):")
        print(chunk)

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
