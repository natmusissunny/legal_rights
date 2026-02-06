"""
安装配置文件
"""
from setuptools import setup, find_packages

setup(
    name="legal_rights",
    version="1.0.2",
    description="法律维权智能助手 - AI-powered legal rights assistant",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/YOUR_GITHUB_USERNAME/legal_rights",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.6.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.1.0",
        "reportlab>=4.0.0",
        "faiss-cpu>=1.8.0",
        "numpy>=1.26.0",
        "anthropic>=0.25.0",
        "openai>=1.0.0",
        "jieba>=0.42.1",
        "rich>=13.7.0",
    ],
    extras_require={
        "domestic": [
            "dashscope",  # 通义千问
            "zhipuai",    # 智谱AI
        ],
    },
    entry_points={
        "console_scripts": [
            "legal-rights=legal_rights.__main__:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
