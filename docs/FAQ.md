# 常见问题 | FAQ

本文档汇总了使用法律维权智能助手时的常见问题和解决方案。

---

## 📥 安装和配置

### Q1: build-kb 报错 "OpenAI API key is required"

**现象**:
```
❌ 索引构建失败: OpenAI API key is required
❌ 错误: 未配置 Embedding API 密钥
```

**原因**:
- `build-kb` 命令需要 Embedding API 来构建向量索引
- 不需要对话模型（LLM）API

**解决方案**:

配置**任意一个** Embedding API密钥:

```env
# 方式1: 智谱AI（推荐，国内）
ZHIPUAI_API_KEY=your-key

# 方式2: OpenAI（国际，需代理）
OPENAI_API_KEY=your-key
```

**最简单的方式** - 使用智谱AI一个密钥完成所有功能:

```bash
# 1. 获取密钥: https://open.bigmodel.cn/
# 2. 配置 .env
echo "ZHIPUAI_API_KEY=your-key" >> .env
echo "LLM_MODE=zhipu" >> .env

# 3. 安装依赖
pip install zhipuai

# 4. 构建知识库
python -m legal_rights build-kb

# 5. 开始使用
python -m legal_rights ask "问题"
```

**注意**: 智谱AI的一个API密钥可以同时用于:
- 对话生成 (LLM)
- 文本向量化 (Embedding)

### Q2: 网页抓取失败 (HTTP 412/404/502)

**现象**:
```
❌ HTTP错误 412: https://m12333.cn/qa/myyuf.html
❌ HTTP错误 404: https://sh.bendibao.com/...
❌ HTTP错误 502: ...
```

**原因**:
- HTTP 412: 网站反爬虫机制
- HTTP 404: 页面不存在或已删除
- HTTP 502: 服务器临时故障

**快速解决方案**:

```bash
# 方法1: 手动下载页面（推荐）
# 1. 浏览器打开该URL
# 2. 按 Ctrl+S 保存网页
# 3. 使用脚本添加到缓存
python scripts/add_to_cache.py "https://m12333.cn/qa/myyuf.html" ~/Downloads/page.html

# 方法2: 使用已有缓存（如果之前抓取成功过）
# build-kb 默认会使用缓存，直接重新执行即可
python -m legal_rights build-kb

# 方法3: 跳过失败的URL
# 编辑 config.py，注释掉失败的URL
```

**详细说明**: 参见 [docs/SCRAPING_ISSUES.md](SCRAPING_ISSUES.md)

### Q2: 提示"ModuleNotFoundError: No module named 'legal_rights'"

**原因**: Python 找不到项目模块

**解决方案**:

```bash
# 确保在项目父目录执行命令
cd /path/to/workspace
python -m legal_rights build-kb

# 或者使用绝对路径
PYTHONPATH=/path/to/workspace python -m legal_rights build-kb
```

### Q2: 提示"未配置 CLAUDE_API_KEY"

**原因**: 环境变量未正确设置

**解决方案**:

方案A - 使用 .env 文件（推荐）:
```bash
cd legal_rights
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥
```

方案B - 导出环境变量:
```bash
export CLAUDE_API_KEY=sk-ant-api03-your-key
export OPENAI_API_KEY=sk-your-key
```

### Q3: pip install 失败

**可能原因和解决方案**:

```bash
# 问题1: Python 版本过低
python --version  # 需要 3.10+
# 解决: 升级 Python

# 问题2: 网络问题
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 使用国内镜像

# 问题3: 权限问题
pip install --user -r requirements.txt
# 使用用户安装模式
```

---

## 🔑 API 密钥相关

### Q4: Claude API 返回 404 错误

**错误信息**: `model: claude-3-5-sonnet-20241022 not found`

**原因**: 模型名称错误或过时

**解决方案**:

检查 `config.py` 中的模型名称，确保使用 2026 年的正确名称：

```python
# config.py
CLAUDE_MODEL: str = "claude-sonnet-4-5"  # ✅ 正确
# 不要使用: "claude-3-5-sonnet-20241022"  # ❌ 过时
```

### Q5: OpenAI API 返回 429 错误（速率限制）

**原因**: API 调用频率过高

**解决方案**:

方案A - 降低速率限制:
```python
# config.py
RATE_LIMIT_PER_SECOND: int = 2  # 降低到 2 次/秒
```

方案B - 使用国内大模型（无速率限制）:
参考 [国内大模型适配指南](DOMESTIC_LLM_GUIDE.md)

### Q6: API 密钥在哪里获取？

**Claude API**:
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 在 API Keys 页面创建密钥

**OpenAI API**:
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 在 API keys 页面创建密钥

**国内大模型**:
- 通义千问: https://dashscope.console.aliyun.com/
- 智谱AI: https://open.bigmodel.cn/

---

## 🏗️ 知识库构建

### Q7: build-kb 命令失败

**常见原因和解决方案**:

```bash
# 原因1: 网络连接问题
# 解决: 检查网络，确保能访问目标网站

# 原因2: API 密钥未配置
# 解决: 参考 Q2

# 原因3: 网页结构变化
# 解决: 使用手动下载法规
python scripts/fetch_core_laws.py --priority 1 --download
```

### Q8: 知识库构建很慢

**正常耗时**: 3-5 分钟

**如果超过 10 分钟**:

1. 检查网络速度
2. 检查 API 速率限制
3. 使用 `--verbose` 查看详细日志:

```bash
python -m legal_rights build-kb --verbose
```

### Q9: 如何更新知识库？

**方法1 - 完全重建**:
```bash
python -m legal_rights build-kb --force
```

**方法2 - 增量更新**:
```bash
# 添加新的 URL
python -m legal_rights add-url "https://new-legal-site.com/article"

# 重新构建索引
python -m legal_rights build-kb
```

---

## 💬 使用问题

### Q10: 回答质量不高，置信度低

**可能原因**:

1. **知识库不全** - 缺少相关法律条文

   解决:
   ```bash
   # 下载核心法规
   python scripts/fetch_core_laws.py --priority 1 --download

   # 重建知识库
   python -m legal_rights build-kb --force
   ```

2. **问题表述不清** - 提问太模糊

   改进示例:
   ```
   ❌ 不好: "公司辞退我怎么办"
   ✅ 更好: "我在公司工作3年，因业绩不好被辞退，应该得到什么补偿？"
   ```

3. **检索参数需要调优**

   修改 `config.py`:
   ```python
   TOP_K_DOCUMENTS: int = 10  # 增加检索文档数
   ```

### Q11: 回答中包含错误信息

**重要**: 本工具仅供参考，不构成法律意见！

**如果发现错误**:

1. 检查知识库来源是否权威
2. 在 [GitHub Issues](https://github.com/yourusername/legal-rights-assistant/issues) 报告问题
3. **务必咨询专业律师**

### Q12: 多轮对话时AI忘记上下文

**原因**: 对话历史超出限制

**解决方案**:

1. 在新对话中重新开始
2. 在问题中重复关键信息

示例:
```
用户: 我在公司工作3年被辞退
AI: [回答...]

用户: 那我应该得到多少补偿？（重复"工作3年"信息）
```

---

## 🇨🇳 国内大模型相关

### Q13: 如何切换到国内大模型？

**详见**: [国内大模型适配指南](DOMESTIC_LLM_GUIDE.md)

**快速步骤**:

1. 安装国内 SDK:
   ```bash
   pip install dashscope zhipuai
   ```

2. 配置 API 密钥:
   ```env
   # .env
   DASHSCOPE_API_KEY=sk-your-qwen-key
   ZHIPUAI_API_KEY=your-zhipu-key
   ```

3. 修改 `config.py` (见指南)

### Q14: 国内大模型和国际版有什么区别？

| 对比项 | 国际版 | 国内版 |
|-------|--------|--------|
| 成本 | $0.011/次 | ¥0.0075/次 (便宜92%) |
| 速度 | 3-5秒 | 1-2秒 (快50%) |
| 网络 | 需要代理 | 直连 |
| 质量 | Claude 4.5 | 通义千问 qwen-max |

**推荐**: 国内用户使用国内大模型

---

## 🐛 错误排查

### Q15: 如何查看详细错误日志？

```bash
# 方法1: 使用 --verbose 参数
python -m legal_rights build-kb --verbose

# 方法2: 重定向到文件
python -m legal_rights build-kb 2>&1 | tee error.log

# 方法3: 启用 Python 调试模式
PYTHONVERBOSE=1 python -m legal_rights build-kb
```

### Q16: 遇到"ConnectionError"或"TimeoutError"

**原因**: 网络连接问题

**解决方案**:

1. 检查网络连接
2. 设置代理（如需要）:
   ```bash
   export HTTP_PROXY=http://127.0.0.1:7890
   export HTTPS_PROXY=http://127.0.0.1:7890
   ```

3. 增加超时时间:
   ```python
   # config.py
   REQUEST_TIMEOUT: int = 60  # 增加到 60 秒
   ```

### Q17: 遇到"MemoryError"

**原因**: 内存不足（构建大知识库时）

**解决方案**:

1. 分批处理:
   ```bash
   # 先处理部分文件
   # 移除一些缓存文件，分两次构建
   ```

2. 减少批处理大小:
   ```python
   # config.py
   EMBED_BATCH_SIZE: int = 5  # 降低到 5
   ```

---

## 📊 性能优化

### Q18: 如何提升回答速度？

**优化建议**:

1. **使用国内大模型** - 响应快 50%

2. **减少检索文档数**:
   ```python
   # config.py
   TOP_K_DOCUMENTS: int = 5  # 从 10 降到 5
   ```

3. **使用 SSD** - 确保 data/ 目录在 SSD 上

4. **启用缓存** (已默认开启)

### Q19: 知识库占用空间太大

**查看空间占用**:
```bash
du -sh data/
```

**优化方案**:

1. 清理缓存:
   ```bash
   rm -rf data/cache/*.html
   # 重新下载时会自动缓存
   ```

2. 不生成 PDF（可选）:
   ```python
   # config.py
   GENERATE_PDF: bool = False
   ```

3. 压缩向量索引（牺牲部分精度）

---

## 🔒 安全和隐私

### Q20: API 密钥会被泄露吗？

**安全措施**:

1. ✅ `.env` 文件已在 `.gitignore` 中
2. ✅ 不要将 `.env` 提交到 Git
3. ✅ 定期轮换 API 密钥

**检查是否泄露**:
```bash
# 检查 Git 历史
git log --all --full-history -- .env

# 如果已提交，立即轮换密钥
```

### Q21: 我的问题会被记录吗？

**本地部署**: ❌ 不会记录

**API 调用**:
- Claude API: 不用于训练，30天后删除
- OpenAI API: 可选择不用于训练

**详见**:
- [Claude 隐私政策](https://www.anthropic.com/privacy)
- [OpenAI 隐私政策](https://openai.com/privacy/)

---

## 🤝 贡献和反馈

### Q22: 如何报告 Bug？

1. 在 [GitHub Issues](https://github.com/yourusername/legal-rights-assistant/issues) 创建 Issue
2. 包含：
   - 详细的问题描述
   - 复现步骤
   - 错误日志
   - 环境信息

### Q23: 如何贡献代码？

详见 [贡献指南](../CONTRIBUTING.md)

---

## 📚 更多资源

- [详细配置指南](SETUP_GUIDE.md)
- [架构说明](ARCHITECTURE.md)
- [RAG工作原理](HOW_IT_WORKS.md)
- [国内大模型适配](DOMESTIC_LLM_GUIDE.md)
- [API使用指南](API_GUIDE.md)

---

**没找到答案？**

在 [GitHub Discussions](https://github.com/yourusername/legal-rights-assistant/discussions) 提问！
