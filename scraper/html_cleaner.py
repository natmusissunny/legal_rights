"""
HTML清洗器
使用 BeautifulSoup 清洗和提取HTML内容
"""
from bs4 import BeautifulSoup, Comment
from typing import Optional
import re


class HTMLCleaner:
    """HTML清洗器"""

    def __init__(self):
        """初始化清洗器"""
        self.unwanted_tags = [
            'script', 'style', 'meta', 'link', 'noscript',
            'iframe', 'object', 'embed', 'applet',
            'nav', 'header', 'footer', 'aside',
            'form', 'input', 'button', 'select', 'textarea'
        ]

        self.unwanted_classes = [
            'ad', 'advertisement', 'banner', 'sidebar',
            'menu', 'navigation', 'nav', 'footer', 'header',
            'comment', 'social', 'share', 'related'
        ]

        self.unwanted_ids = [
            'ad', 'ads', 'advertisement', 'sidebar',
            'menu', 'navigation', 'footer', 'header',
            'comment', 'comments'
        ]

    def clean(self, html: str) -> str:
        """
        清洗HTML

        Args:
            html: 原始HTML

        Returns:
            清洗后的HTML
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, 'lxml')

        # 1. 移除注释
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. 移除不需要的标签
        for tag_name in self.unwanted_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 3. 移除带有特定class的元素
        for class_name in self.unwanted_classes:
            for tag in soup.find_all(class_=re.compile(class_name, re.I)):
                tag.decompose()

        # 4. 移除带有特定id的元素
        for id_name in self.unwanted_ids:
            for tag in soup.find_all(id=re.compile(id_name, re.I)):
                tag.decompose()

        # 5. 移除空标签
        self._remove_empty_tags(soup)

        return str(soup)

    def _remove_empty_tags(self, soup: BeautifulSoup):
        """递归移除空标签"""
        changed = True
        while changed:
            changed = False
            for tag in soup.find_all():
                # 跳过某些标签
                if tag.name in ['br', 'hr', 'img']:
                    continue

                # 如果标签内容为空且没有子标签
                if not tag.get_text(strip=True) and not tag.find_all():
                    tag.decompose()
                    changed = True

    def extract_text(self, html: str) -> str:
        """
        提取纯文本

        Args:
            html: HTML内容

        Returns:
            纯文本内容
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, 'lxml')

        # 移除不需要的标签
        for tag_name in self.unwanted_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 获取文本
        text = soup.get_text(separator='\n', strip=True)

        # 清理多余的空白
        text = re.sub(r'\n\s*\n', '\n\n', text)  # 多个空行变成两个
        text = re.sub(r' +', ' ', text)  # 多个空格变成一个

        return text.strip()

    def extract_main_content(self, html: str) -> Optional[str]:
        """
        提取主要内容

        Args:
            html: HTML内容

        Returns:
            主要内容的HTML，如果找不到返回None
        """
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')

        # 尝试多种策略找到主要内容
        main_content = None

        # 策略1: 查找常见的内容容器
        content_selectors = [
            'article',
            '[class*="content"]',
            '[class*="main"]',
            '[class*="article"]',
            '[id*="content"]',
            '[id*="main"]',
            '[id*="article"]',
            'main',
            '.content',
            '#content',
            '.main-content',
            '#main-content'
        ]

        for selector in content_selectors:
            try:
                if selector.startswith('[') or selector.startswith('.') or selector.startswith('#'):
                    elements = soup.select(selector)
                else:
                    elements = soup.find_all(selector)

                if elements:
                    # 选择最长的内容
                    main_content = max(elements, key=lambda x: len(x.get_text()))
                    break
            except:
                continue

        # 策略2: 如果没找到，查找最长的div
        if not main_content:
            divs = soup.find_all('div')
            if divs:
                # 过滤掉明显是导航、侧边栏的div
                valid_divs = []
                for div in divs:
                    div_class = ' '.join(div.get('class', [])).lower()
                    div_id = (div.get('id') or '').lower()

                    # 跳过不需要的div
                    skip = False
                    for unwanted in self.unwanted_classes + self.unwanted_ids:
                        if unwanted in div_class or unwanted in div_id:
                            skip = True
                            break

                    if not skip:
                        valid_divs.append(div)

                if valid_divs:
                    main_content = max(valid_divs, key=lambda x: len(x.get_text()))

        # 策略3: 如果还是没找到，返回body
        if not main_content:
            main_content = soup.find('body')

        if main_content:
            return str(main_content)

        return None

    def clean_and_extract(self, html: str) -> tuple[str, str]:
        """
        清洗并提取内容

        Args:
            html: 原始HTML

        Returns:
            (清洗后的HTML, 纯文本)
        """
        # 先提取主要内容
        main_content = self.extract_main_content(html)
        if not main_content:
            main_content = html

        # 清洗HTML
        cleaned_html = self.clean(main_content)

        # 提取纯文本
        text = self.extract_text(cleaned_html)

        return cleaned_html, text


def test_cleaner():
    """测试清洗器"""
    sample_html = """
    <html>
    <head>
        <title>测试页面</title>
        <script>console.log('test');</script>
        <style>.test { color: red; }</style>
    </head>
    <body>
        <nav>导航栏</nav>
        <div class="advertisement">广告</div>
        <article>
            <h1>标题</h1>
            <p>这是一段正文内容。</p>
            <div class="social-share">分享</div>
        </article>
        <footer>页脚</footer>
    </body>
    </html>
    """

    cleaner = HTMLCleaner()

    print("原始HTML:")
    print("=" * 60)
    print(sample_html)

    cleaned_html, text = cleaner.clean_and_extract(sample_html)

    print("\n清洗后的HTML:")
    print("=" * 60)
    print(cleaned_html)

    print("\n提取的文本:")
    print("=" * 60)
    print(text)


if __name__ == "__main__":
    test_cleaner()
