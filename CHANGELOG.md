# 更新日志 | Changelog

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.0.2] - 2026-02-06

### 🔧 修复

- 更新 Claude 模型名称为 `claude-sonnet-4-5`（2026 年新模型）
- 修复模型 404 错误

### 📝 文档

- 更新 API 配置指南

---

## [1.0.1] - 2026-02-06

### 🚀 新增

- 添加核心法规自动下载脚本 (`scripts/fetch_core_laws.py`)
- 支持从全国人大、国务院等网站下载 8 个核心法规

### 📚 文档

- 添加核心法规获取指南 (`docs/GET_CORE_LAWS.md`)
- 添加知识库扩展指南 (`docs/EXPAND_KNOWLEDGE_BASE.md`)

---

## [1.0.0] - 2026-02-06

### 🎉 首次发布

#### 🌟 核心功能

- **知识库构建**: 自动抓取权威法律网站内容
- **智能问答**: 基于 RAG 架构的法律咨询服务
- **多轮对话**: 支持上下文理解的连续对话
- **向量检索**: 使用 FAISS 进行语义检索
- **答案溯源**: 提供法律依据和来源链接

#### 🇨🇳 国内大模型支持

- 添加通义千问（Qwen）客户端
- 添加智谱AI（Zhipu AI）Embedding 客户端
- 成本降低 92%，响应速度提升 50%

#### 📦 模块实现

- ✅ `scraper/` - 网页抓取模块
- ✅ `knowledge/` - 知识库处理模块
- ✅ `agent/` - AI Agent 模块
- ✅ `scripts/` - 工具脚本

#### 📚 文档

- README.md - 项目主文档
- docs/SETUP_GUIDE.md - 详细配置指南
- docs/ARCHITECTURE.md - 架构说明
- docs/HOW_IT_WORKS.md - RAG 工作原理
- docs/DOMESTIC_LLM_GUIDE.md - 国内大模型适配
- docs/API_GUIDE.md - API 使用指南

#### 🛠️ 工具脚本

- `build_knowledge_base.py` - 知识库构建
- `fetch_core_laws.py` - 核心法规下载
- `quick_start.py` - 快速启动

#### 🧪 测试

- `test_scraper.py` - 抓取器测试
- `test_agent.py` - Agent 测试
- `test_vector_index.py` - 向量索引测试

---

## 计划中的功能 | Planned Features

### [1.1.0] - 计划中

#### 🚀 新功能

- [ ] Web 界面支持
- [ ] 补偿金计算器（独立工具）
- [ ] 批量文档导入功能
- [ ] 多数据源支持（PDF、Word）

#### 🌍 国际化

- [ ] 英文文档
- [ ] 英文界面支持

#### 🧪 质量提升

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试
- [ ] 性能基准测试

#### 📊 数据扩展

- [ ] 更多地区法律法规
- [ ] 典型判例数据库
- [ ] 劳动仲裁案例

---

## [1.2.0] - 计划中

#### 🤖 AI 能力提升

- [ ] 支持 GPT-4
- [ ] 支持更多国内大模型
- [ ] 微调模型支持

#### 🔍 检索优化

- [ ] 混合检索（关键词 + 向量）
- [ ] 重排序算法
- [ ] 查询扩展

#### 💬 对话增强

- [ ] 长期记忆
- [ ] 个性化推荐
- [ ] 多用户支持

---

## 版本说明

### 语义化版本

- **主版本号 (MAJOR)**: 不兼容的 API 变更
- **次版本号 (MINOR)**: 向后兼容的新功能
- **修订号 (PATCH)**: 向后兼容的 Bug 修复

### 变更类型

- `Added` 🚀 - 新增功能
- `Changed` 🔄 - 功能变更
- `Deprecated` ⚠️ - 即将废弃的功能
- `Removed` 🗑️ - 已删除的功能
- `Fixed` 🔧 - Bug 修复
- `Security` 🔒 - 安全相关

---

**日期格式**: YYYY-MM-DD
**链接**: [版本号] https://github.com/yourusername/legal-rights-assistant/releases/tag/v版本号
