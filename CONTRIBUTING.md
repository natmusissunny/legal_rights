# 贡献指南 | Contributing Guide

感谢您对法律维权智能助手项目的关注！我们欢迎各种形式的贡献。

Thank you for your interest in the Legal Rights AI Assistant! We welcome all kinds of contributions.

---

## 🤝 如何贡献

### 报告问题 (Bug Reports)

如果您发现了 bug，请：

1. 在 [GitHub Issues](https://github.com/yourusername/legal-rights-assistant/issues) 中搜索是否已有相同问题
2. 如果没有，创建新 Issue，并包含：
   - 详细的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 您的环境信息（Python 版本、操作系统等）
   - 相关日志或错误信息

**Issue 模板：**

```markdown
**问题描述**
简要描述问题

**复现步骤**
1. 执行命令：python -m legal_rights ...
2. 输入内容：...
3. 观察到错误：...

**预期行为**
描述您期望发生什么

**实际行为**
描述实际发生了什么

**环境信息**
- OS: [e.g., macOS 14.0]
- Python 版本: [e.g., 3.10.5]
- 项目版本: [e.g., 1.0.2]

**错误日志**
```
粘贴相关错误信息
```
```

### 功能建议 (Feature Requests)

如果您有好的想法，请：

1. 在 [GitHub Discussions](https://github.com/yourusername/legal-rights-assistant/discussions) 中分享
2. 说明：
   - 功能的使用场景
   - 如何解决现有问题
   - 可能的实现方案

### 提交代码 (Pull Requests)

我们欢迎所有形式的代码贡献！

**开发流程：**

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   git clone https://github.com/YOUR_USERNAME/legal-rights-assistant.git
   cd legal-rights-assistant
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **进行开发**
   - 遵循代码风格指南（见下方）
   - 添加必要的测试
   - 更新相关文档

4. **运行测试**
   ```bash
   # 安装开发依赖
   pip install -r requirements-dev.txt

   # 运行测试
   python -m pytest tests/

   # 代码格式化
   black .
   isort .

   # 类型检查
   mypy .

   # 代码检查
   flake8 .
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复Bug描述"
   ```

6. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 在 GitHub 上打开 Pull Request
   - 填写 PR 描述模板
   - 等待代码审查

---

## 📋 代码风格指南

### Python 代码规范

我们遵循 [PEP 8](https://pep8.org/) 风格指南，并使用以下工具：

- **Black**: 代码格式化（line length: 100）
- **isort**: 导入语句排序
- **flake8**: 代码检查
- **mypy**: 类型检查

### 命名规范

```python
# 模块名：小写+下划线
web_scraper.py

# 类名：大驼峰
class LegalAgent:
    pass

# 函数名：小写+下划线
def build_knowledge_base():
    pass

# 常量：大写+下划线
MAX_RETRIES = 3

# 私有方法：下划线开头
def _internal_method(self):
    pass
```

### 类型注解

所有新代码应包含类型注解：

```python
from typing import List, Optional

def embed_text(text: str, model: str = "embedding-2") -> List[float]:
    """向量化文本

    Args:
        text: 输入文本
        model: Embedding模型名称

    Returns:
        向量列表
    """
    pass
```

### 文档字符串

使用 Google 风格的 docstring：

```python
def retrieve_documents(query: str, top_k: int = 5) -> List[Document]:
    """检索相关文档

    Args:
        query: 查询文本
        top_k: 返回文档数量

    Returns:
        相关文档列表，按相似度排序

    Raises:
        ValueError: 如果 top_k < 1

    Example:
        >>> docs = retrieve_documents("劳动合同法", top_k=3)
        >>> len(docs)
        3
    """
    pass
```

---

## 🧪 测试指南

### 编写测试

所有新功能都应包含测试：

```python
# tests/test_embedding_client.py
import pytest
from legal_rights.knowledge.embedding_client import EmbeddingClient

def test_embed_single_text():
    """测试单个文本向量化"""
    client = EmbeddingClient(api_key="test-key")
    vector = client.embed("测试文本")

    assert isinstance(vector, list)
    assert len(vector) == 1536  # OpenAI embedding dimension
    assert all(isinstance(v, float) for v in vector)

def test_embed_batch():
    """测试批量向量化"""
    client = EmbeddingClient(api_key="test-key")
    texts = ["文本1", "文本2", "文本3"]
    vectors = client.embed_batch(texts)

    assert len(vectors) == 3
    assert all(len(v) == 1536 for v in vectors)
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_embedding_client.py

# 运行特定测试函数
pytest tests/test_embedding_client.py::test_embed_single_text

# 显示详细输出
pytest -v

# 显示覆盖率
pytest --cov=legal_rights --cov-report=html
```

---

## 📝 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链更新

### 示例

```
feat(agent): 添加多轮对话支持

- 实现对话历史管理
- 添加上下文压缩功能
- 更新 Prompt 模板

Closes #123
```

```
fix(scraper): 修复HTML解析错误

修复当网页包含特殊字符时解析失败的问题

Fixes #456
```

---

## 🌳 分支策略

- `main`: 稳定版本，受保护
- `develop`: 开发分支
- `feature/*`: 新功能分支
- `fix/*`: Bug 修复分支
- `docs/*`: 文档更新分支

---

## 📚 文档贡献

文档和代码同样重要！如果您发现文档错误或不清晰，请：

1. 直接修改 `docs/` 目录中的 Markdown 文件
2. 提交 Pull Request
3. 说明改进内容

### 文档规范

- 使用清晰简洁的语言
- 提供代码示例
- 包含截图（如有必要）
- 检查拼写和语法

---

## 🎨 UI/UX 改进

如果您有界面或用户体验改进建议：

1. 在 GitHub Discussions 中发起讨论
2. 提供设计稿或示例（如有）
3. 说明改进的理由

---

## 🌍 国际化 (i18n)

我们欢迎翻译贡献！

当前支持语言：
- 🇨🇳 简体中文
- 🇺🇸 English

如需添加新语言：

1. 在 `docs/` 创建语言子目录（如 `docs/en/`）
2. 翻译核心文档
3. 更新 README.md 中的语言链接

---

## ⚖️ 许可协议

贡献代码即表示您同意：

1. 您的贡献将以 MIT License 发布
2. 您拥有贡献代码的版权或已获授权
3. 您的贡献不侵犯第三方权利

---

## 💬 社区交流

- **GitHub Discussions**: 讨论功能、想法、问题
- **GitHub Issues**: 报告 Bug、追踪任务
- **Pull Requests**: 代码审查和讨论

---

## 🙏 致谢

感谢每一位贡献者！您的贡献让这个项目更好。

---

**有疑问？**

在 [GitHub Discussions](https://github.com/yourusername/legal-rights-assistant/discussions) 中提问，社区会帮助您！
