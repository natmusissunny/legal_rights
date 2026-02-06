"""
内容解析器
将清洗后的HTML解析成结构化内容
"""
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import re

from ..models import LegalSection, StructuredContent


class ContentParser:
    """内容解析器"""

    def __init__(self):
        """初始化解析器"""
        # 标题标签层级映射
        self.heading_levels = {
            'h1': 1, 'h2': 2, 'h3': 3,
            'h4': 4, 'h5': 5, 'h6': 6
        }

    def parse(self, html: str, url: str, title: str = None) -> StructuredContent:
        """
        解析HTML为结构化内容

        Args:
            html: 清洗后的HTML
            url: 来源URL
            title: 文档标题（如果为None则自动提取）

        Returns:
            结构化内容
        """
        if not html:
            return StructuredContent(
                url=url,
                title=title or "未命名文档",
                sections=[],
                scraped_at=datetime.now()
            )

        soup = BeautifulSoup(html, 'lxml')

        # 提取标题
        if not title:
            title = self._extract_title(soup)

        # 解析章节
        sections = self._parse_sections(soup)

        # 如果没有找到章节结构，将整个内容作为一个章节
        if not sections:
            content = soup.get_text(separator='\n', strip=True)
            if content:
                sections = [LegalSection(
                    title="正文",
                    content=content,
                    subsections=[],
                    level=1
                )]

        return StructuredContent(
            url=url,
            title=title,
            sections=sections,
            scraped_at=datetime.now()
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取文档标题"""
        # 尝试从h1标签提取
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # 尝试从title标签提取
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)

        # 尝试从meta标签提取
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content']

        return "未命名文档"

    def _parse_sections(self, soup: BeautifulSoup) -> List[LegalSection]:
        """解析章节结构"""
        sections = []
        current_section = None
        section_stack = []  # 用于处理嵌套章节

        # 找到所有标题和段落
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'li']):
            tag_name = element.name

            # 处理标题
            if tag_name in self.heading_levels:
                level = self.heading_levels[tag_name]
                title = element.get_text(strip=True)

                if not title:
                    continue

                # 创建新章节
                new_section = LegalSection(
                    title=title,
                    content="",
                    subsections=[],
                    level=level
                )

                # 处理嵌套关系
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    # 作为子章节添加
                    section_stack[-1].subsections.append(new_section)
                else:
                    # 作为顶层章节添加
                    sections.append(new_section)

                section_stack.append(new_section)
                current_section = new_section

            # 处理内容
            elif current_section:
                text = element.get_text(strip=True)
                if text:
                    if current_section.content:
                        current_section.content += "\n\n" + text
                    else:
                        current_section.content = text

        return sections

    def _identify_legal_articles(self, text: str) -> List[str]:
        """识别法律条文"""
        # 匹配法律条文的正则表达式
        patterns = [
            r'《[^》]+》第[零一二三四五六七八九十百千\d]+条',  # 《劳动合同法》第38条
            r'第[零一二三四五六七八九十百千\d]+条',  # 第38条
            r'[零一二三四五六七八九十百千\d]+、',  # 1、2、3、
        ]

        articles = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            articles.extend(matches)

        return list(set(articles))  # 去重

    def extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词

        Args:
            text: 文本内容

        Returns:
            关键词列表
        """
        # 法律相关关键词
        legal_keywords = [
            '经济补偿', '赔偿金', '解除劳动合同', '终止劳动合同',
            '违法解除', '协商解除', '裁员', '辞退', '离职',
            'N+1', '2N', '补偿金', '双倍赔偿',
            '劳动仲裁', '劳动争议', '维权', '诉讼',
            '工龄', '工资', '加班费', '社保', '公积金',
            '试用期', '服务期', '竞业限制', '保密协议',
            '无固定期限', '固定期限', '劳务派遣'
        ]

        found_keywords = []
        text_lower = text.lower()

        for keyword in legal_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords

    def merge_short_sections(
        self,
        sections: List[LegalSection],
        min_length: int = 50
    ) -> List[LegalSection]:
        """
        合并过短的章节

        Args:
            sections: 章节列表
            min_length: 最小章节长度

        Returns:
            合并后的章节列表
        """
        if not sections:
            return sections

        merged = []
        buffer_section = None

        for section in sections:
            content_length = len(section.content)

            if content_length < min_length and not section.subsections:
                # 章节太短，尝试合并
                if buffer_section:
                    buffer_section.content += "\n\n" + section.title + "\n" + section.content
                else:
                    buffer_section = section
            else:
                # 章节足够长，先保存buffer
                if buffer_section:
                    merged.append(buffer_section)
                    buffer_section = None

                # 递归处理子章节
                if section.subsections:
                    section.subsections = self.merge_short_sections(
                        section.subsections,
                        min_length
                    )

                merged.append(section)

        # 保存最后的buffer
        if buffer_section:
            merged.append(buffer_section)

        return merged


def test_parser():
    """测试解析器"""
    sample_html = """
    <html>
    <body>
        <h1>离职经济补偿指南</h1>
        <h2>一、经济补偿的法律依据</h2>
        <p>根据《劳动合同法》第46条规定，用人单位应当向劳动者支付经济补偿。</p>
        <h3>1.1 补偿标准</h3>
        <p>经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。</p>
        <h2>二、如何计算补偿金</h2>
        <p>补偿金 = 工作年限 × 月平均工资</p>
        <h3>2.1 N+1补偿</h3>
        <p>用人单位未提前30日通知的，应额外支付一个月工资作为代通知金。</p>
    </body>
    </html>
    """

    parser = ContentParser()
    structured = parser.parse(
        html=sample_html,
        url="https://example.com/test",
        title=None
    )

    print("解析结果:")
    print("=" * 60)
    print(f"标题: {structured.title}")
    print(f"URL: {structured.url}")
    print(f"章节数: {len(structured.sections)}")
    print()

    def print_sections(sections, indent=0):
        for section in sections:
            prefix = "  " * indent
            print(f"{prefix}[Lv{section.level}] {section.title}")
            if section.content:
                content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
                print(f"{prefix}     {content_preview}")
            if section.subsections:
                print_sections(section.subsections, indent + 1)

    print_sections(structured.sections)


if __name__ == "__main__":
    test_parser()
