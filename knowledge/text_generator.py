"""
文本文档生成器
将结构化内容生成为格式化的文本文档（Markdown格式）
作为PDF生成的替代方案（避免中文字体问题）
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..models import StructuredContent, LegalSection
from ..config import Config


class TextGenerator:
    """文本文档生成器"""

    def __init__(self):
        """初始化生成器"""
        self.output_dir = Config.KNOWLEDGE_DIR

    def _sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        # 移除不允许的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')

        # 限制长度
        if len(title) > 50:
            title = title[:50]

        return title.strip()

    def generate(
        self,
        content: StructuredContent,
        output_path: Optional[Path] = None,
        format: str = 'md'
    ) -> Path:
        """
        生成文本文档

        Args:
            content: 结构化内容
            output_path: 输出路径（如果为None则自动生成）
            format: 输出格式 ('md' for Markdown, 'txt' for plain text)

        Returns:
            生成的文件路径
        """
        # 确定输出路径
        if output_path is None:
            filename = self._sanitize_filename(content.title) + f'.{format}'
            output_path = self.output_dir / filename

        print(f"📄 生成文档: {content.title}")
        print(f"   输出: {output_path}")

        # 生成内容
        if format == 'md':
            text = self._generate_markdown(content)
        else:
            text = self._generate_plain_text(content)

        # 保存文件
        output_path.write_text(text, encoding='utf-8')

        file_size = output_path.stat().st_size
        print(f"   ✅ 生成完成 ({file_size:,} 字节)")

        return output_path

    def _generate_markdown(self, content: StructuredContent) -> str:
        """生成Markdown格式"""
        lines = []

        # 标题
        lines.append(f"# {content.title}\n")

        # 元数据
        lines.append("---\n")
        lines.append(f"**来源**: {content.url}\n")
        lines.append(f"**抓取时间**: {content.scraped_at.strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        lines.append(f"**章节数**: {len(content.sections)}\n")
        lines.append("---\n")

        # 目录
        lines.append("\n## 目录\n")
        for section in content.sections:
            self._add_section_to_toc_md(section, lines, level=1)

        lines.append("\n---\n")

        # 内容
        for section in content.sections:
            self._add_section_md(section, lines)

        # 页脚
        lines.append("\n---\n")
        lines.append("*本文档由法律维权智能助手自动生成*\n")
        lines.append("*内容仅供参考，具体法律问题请咨询专业律师*\n")

        return "\n".join(lines)

    def _add_section_to_toc_md(self, section: LegalSection, lines: List[str], level: int):
        """添加章节到目录（Markdown）"""
        indent = "  " * (level - 1)
        lines.append(f"{indent}- {section.title}")

        for subsection in section.subsections:
            self._add_section_to_toc_md(subsection, lines, level + 1)

    def _add_section_md(self, section: LegalSection, lines: List[str]):
        """添加章节内容（Markdown）"""
        # 标题
        heading_marker = "#" * (section.level + 1)  # h1已用于文档标题，从h2开始
        lines.append(f"\n{heading_marker} {section.title}\n")

        # 内容
        if section.content:
            lines.append(section.content + "\n")

        # 递归处理子章节
        for subsection in section.subsections:
            self._add_section_md(subsection, lines)

    def _generate_plain_text(self, content: StructuredContent) -> str:
        """生成纯文本格式"""
        lines = []

        # 标题
        lines.append("=" * 80)
        lines.append(content.title.center(80))
        lines.append("=" * 80)
        lines.append("")

        # 元数据
        lines.append(f"来源: {content.url}")
        lines.append(f"抓取时间: {content.scraped_at.strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append(f"章节数: {len(content.sections)}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

        # 目录
        lines.append("目录".center(80))
        lines.append("")
        for section in content.sections:
            self._add_section_to_toc_txt(section, lines, level=1)

        lines.append("")
        lines.append("=" * 80)
        lines.append("")

        # 内容
        for section in content.sections:
            self._add_section_txt(section, lines)

        # 页脚
        lines.append("")
        lines.append("-" * 80)
        lines.append("本文档由法律维权智能助手自动生成")
        lines.append("内容仅供参考，具体法律问题请咨询专业律师")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _add_section_to_toc_txt(self, section: LegalSection, lines: List[str], level: int):
        """添加章节到目录（纯文本）"""
        indent = "  " * (level - 1)
        prefix = "·" * level
        lines.append(f"{indent}{prefix} {section.title}")

        for subsection in section.subsections:
            self._add_section_to_toc_txt(subsection, lines, level + 1)

    def _add_section_txt(self, section: LegalSection, lines: List[str]):
        """添加章节内容（纯文本）"""
        # 标题
        lines.append("")
        title_line = "  " * (section.level - 1) + section.title
        lines.append(title_line)
        lines.append("-" * len(title_line.encode('utf-8')))  # 下划线
        lines.append("")

        # 内容
        if section.content:
            # 添加缩进
            content_lines = section.content.split('\n')
            indent = "  " * section.level
            for line in content_lines:
                if line.strip():
                    lines.append(indent + line)
                else:
                    lines.append("")

        # 递归处理子章节
        for subsection in section.subsections:
            self._add_section_txt(subsection, lines)

    def generate_batch(
        self,
        contents: List[StructuredContent],
        format: str = 'md'
    ) -> List[Path]:
        """
        批量生成文档

        Args:
            contents: 结构化内容列表
            format: 输出格式

        Returns:
            生成的文件路径列表
        """
        print(f"\n📚 批量生成 {len(contents)} 个文档 (格式: {format})")
        print("=" * 70)

        output_paths = []

        for i, content in enumerate(contents, 1):
            print(f"\n[{i}/{len(contents)}]")
            try:
                path = self.generate(content, format=format)
                output_paths.append(path)
            except Exception as e:
                print(f"   ❌ 生成失败: {e}")

        print("\n" + "=" * 70)
        print(f"✅ 完成: 成功 {len(output_paths)}/{len(contents)}")

        return output_paths
