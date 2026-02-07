#!/bin/bash

# 法律维权智能助手 - 一键安装脚本 v1.1.0
# 支持多种大模型配置

set -e

echo "=========================================="
echo "🚀 法律维权智能助手 - 一键安装 v1.1.0"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python版本
echo "📋 步骤 1/6: 检查 Python 环境"
echo "------------------------------------------"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3${NC}"
    echo "请先安装 Python 3.10 或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"

# 检查 Python 版本是否 >= 3.10
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 版本过低（需要 >= 3.10）${NC}"
    echo "当前版本: $PYTHON_VERSION"
    echo "请升级 Python"
    exit 1
fi

echo ""

# 安装依赖
echo "📦 步骤 2/6: 安装依赖包"
echo "------------------------------------------"

echo "正在安装基础依赖..."
pip3 install -r requirements.txt --quiet

echo -e "${GREEN}✅ 基础依赖已安装${NC}"

echo ""

# 配置 .env 文件
echo "⚙️  步骤 3/6: 配置 API 密钥"
echo "------------------------------------------"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  检测到已存在 .env 文件${NC}"
    read -p "是否覆盖? (y/n，默认 n): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "保留现有 .env 文件"
        HAS_ENV=true
    else
        rm .env
        HAS_ENV=false
    fi
else
    HAS_ENV=false
fi

if [ "$HAS_ENV" != "true" ]; then
    echo ""
    echo -e "${BLUE}请选择配置方案:${NC}"
    echo ""
    echo "  ${GREEN}1) 智谱AI 单一密钥${NC} ⭐ 推荐新手"
    echo "     - 只需1个密钥"
    echo "     - 配置最简单"
    echo "     - 成本: ¥0.01/次"
    echo ""
    echo "  ${GREEN}2) DeepSeek + 智谱AI${NC} 💰 最便宜"
    echo "     - 需要2个密钥"
    echo "     - 成本: ¥0.005/次"
    echo "     - 质量很好"
    echo ""
    echo "  ${GREEN}3) 通义千问 + 智谱AI${NC} 🏢 企业稳定"
    echo "     - 需要2个密钥"
    echo "     - 成本: ¥0.02/次"
    echo "     - 阿里云背景"
    echo ""
    echo "  4) Claude + OpenAI (国际版，需代理)"
    echo "     - 需要2个密钥"
    echo "     - 成本: $0.013/次"
    echo "     - 质量最高"
    echo ""
    echo "  ${BLUE}5) LiteLLM 统一接口${NC} 🔧 高级用户"
    echo "     - 统一管理所有模型"
    echo "     - 支持100+模型"
    echo "     - 负载均衡、成本追踪"
    echo "     - 需要配置代理或模型密钥"
    echo ""
    echo "  6) 跳过配置（稍后手动配置）"
    echo ""
    read -p "选择 (1-6，默认 1): " config_choice

    config_choice=${config_choice:-1}

    if [ "$config_choice" = "1" ]; then
        # 智谱AI 单一密钥
        echo ""
        echo -e "${BLUE}配置智谱AI (一个密钥搞定所有功能):${NC}"
        echo ""
        echo "📌 如何获取:"
        echo "   1. 访问: https://open.bigmodel.cn/"
        echo "   2. 注册并登录"
        echo "   3. 进入「API Keys」页面"
        echo "   4. 创建新的 API Key"
        echo ""
        read -p "  智谱AI API Key: " zhipu_key

        # 检查是否已安装zhipuai
        echo ""
        echo "正在安装智谱AI SDK..."
        pip3 install zhipuai --quiet

        cat > .env << EOF
# 智谱AI 配置（单一密钥方案）
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: 使用智谱AI
LLM_MODE=zhipu

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（智谱AI）${NC}"
        echo -e "${BLUE}💡 这个密钥可以同时用于对话和向量化${NC}"

    elif [ "$config_choice" = "2" ]; then
        # DeepSeek + 智谱AI
        echo ""
        echo -e "${BLUE}配置 DeepSeek + 智谱AI (最便宜方案):${NC}"
        echo ""
        echo "📌 如何获取:"
        echo "   DeepSeek: https://platform.deepseek.com/"
        echo "   智谱AI: https://open.bigmodel.cn/"
        echo ""
        read -p "  DeepSeek API Key: " deepseek_key
        read -p "  智谱AI API Key: " zhipu_key

        echo ""
        echo "正在安装智谱AI SDK..."
        pip3 install zhipuai --quiet

        cat > .env << EOF
# DeepSeek + 智谱AI 配置（最便宜方案）
DEEPSEEK_API_KEY=$deepseek_key
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: 自动选择（优先DeepSeek）
LLM_MODE=auto

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（DeepSeek + 智谱AI）${NC}"
        echo -e "${BLUE}💡 DeepSeek用于对话，智谱AI用于向量化${NC}"

    elif [ "$config_choice" = "3" ]; then
        # 通义千问 + 智谱AI
        echo ""
        echo -e "${BLUE}配置 通义千问 + 智谱AI (国内稳定方案):${NC}"
        echo ""
        echo "📌 如何获取:"
        echo "   通义千问: https://dashscope.console.aliyun.com/"
        echo "   智谱AI: https://open.bigmodel.cn/"
        echo ""
        read -p "  通义千问 API Key: " qwen_key
        read -p "  智谱AI API Key: " zhipu_key

        echo ""
        echo "正在安装国内大模型SDK..."
        pip3 install dashscope zhipuai --quiet

        cat > .env << EOF
# 通义千问 + 智谱AI 配置（国内稳定方案）
DASHSCOPE_API_KEY=$qwen_key
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: 自动选择（优先通义千问）
LLM_MODE=auto

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（通义千问 + 智谱AI）${NC}"
        echo -e "${BLUE}💡 通义千问用于对话，智谱AI用于向量化${NC}"

    elif [ "$config_choice" = "4" ]; then
        # Claude + OpenAI
        echo ""
        echo -e "${BLUE}配置 Claude + OpenAI (国际版):${NC}"
        echo ""
        echo "⚠️  注意: 需要代理才能访问"
        echo ""
        echo "📌 如何获取:"
        echo "   Claude: https://console.anthropic.com/"
        echo "   OpenAI: https://platform.openai.com/"
        echo ""
        read -p "  Claude API Key: " claude_key
        read -p "  OpenAI API Key: " openai_key

        cat > .env << EOF
# Claude + OpenAI 配置（国际版）
CLAUDE_API_KEY=$claude_key
OPENAI_API_KEY=$openai_key

# LLM模式: 自动选择（优先Claude）
LLM_MODE=auto

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（Claude + OpenAI）${NC}"
        echo -e "${BLUE}💡 Claude用于对话，OpenAI用于向量化${NC}"

    elif [ "$config_choice" = "5" ]; then
        # LiteLLM 统一接口
        echo ""
        echo -e "${BLUE}配置 LiteLLM 统一接口 (高级功能):${NC}"
        echo ""
        echo "LiteLLM 支持两种使用方式:"
        echo ""
        echo "  1) 使用 LiteLLM 代理服务器 (推荐)"
        echo "     - 需要先启动 LiteLLM 代理"
        echo "     - 支持负载均衡、成本追踪等高级功能"
        echo ""
        echo "  2) 直接使用 LiteLLM"
        echo "     - 无需代理，配置简单"
        echo "     - 需要配置对应模型的 API 密钥"
        echo ""
        read -p "选择 (1/2，默认 1): " litellm_mode
        litellm_mode=${litellm_mode:-1}

        if [ "$litellm_mode" = "1" ]; then
            # 使用代理
            echo ""
            echo "📌 使用 LiteLLM 代理模式"
            echo ""
            read -p "  LiteLLM 代理地址 (默认 http://localhost:4000): " litellm_base
            litellm_base=${litellm_base:-http://localhost:4000}
            read -p "  LiteLLM 模型名称 (如 gpt-4, claude): " litellm_model
            read -p "  LiteLLM API Key (可选，按Enter跳过): " litellm_key
            read -p "  智谱AI API Key (用于向量化): " zhipu_key

            echo ""
            echo "正在安装 LiteLLM 和依赖..."
            pip3 install 'litellm[proxy]' zhipuai --quiet

            cat > .env << EOF
# LiteLLM 代理配置（高级功能）
LITELLM_MODEL=$litellm_model
LITELLM_API_BASE=$litellm_base
$([ -n "$litellm_key" ] && echo "LITELLM_API_KEY=$litellm_key" || echo "# LITELLM_API_KEY=")

# Embedding 配置
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: 使用 LiteLLM
LLM_MODE=litellm

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
            echo -e "${GREEN}✅ .env 文件已创建（LiteLLM 代理模式）${NC}"
            echo ""
            echo -e "${YELLOW}⚠️  使用前需要启动 LiteLLM 代理:${NC}"
            echo "   1. 创建 litellm_config.yaml 配置文件"
            echo "   2. 运行: litellm --config litellm_config.yaml --port 4000"
            echo ""
            echo "📖 详细文档: docs/LITELLM_INTEGRATION.md"

        else
            # 直接使用
            echo ""
            echo "📌 使用 LiteLLM 直接模式"
            echo ""
            read -p "  LiteLLM 模型名称 (如 claude-3-opus-20240229): " litellm_model
            echo ""
            echo "需要配置对应模型的 API 密钥:"
            echo "  - 如果使用 Claude: 需要 ANTHROPIC_API_KEY"
            echo "  - 如果使用 OpenAI: 需要 OPENAI_API_KEY"
            echo "  - 如果使用 通义千问: 需要 DASHSCOPE_API_KEY"
            echo ""
            read -p "  对应模型的 API Key (环境变量会自动读取): " model_key_name
            read -p "  API Key 值: " model_key_value
            read -p "  智谱AI API Key (用于向量化): " zhipu_key

            echo ""
            echo "正在安装 LiteLLM 和依赖..."
            pip3 install litellm zhipuai --quiet

            cat > .env << EOF
# LiteLLM 直接模式配置
LITELLM_MODEL=$litellm_model

# 对应模型的 API 密钥
$model_key_name=$model_key_value

# Embedding 配置
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: 使用 LiteLLM
LLM_MODE=litellm

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
            echo -e "${GREEN}✅ .env 文件已创建（LiteLLM 直接模式）${NC}"
            echo -e "${BLUE}💡 LiteLLM 会自动读取环境变量中的模型密钥${NC}"
            echo ""
            echo "📖 详细文档: docs/LITELLM_INTEGRATION.md"
        fi

    else
        cp .env.example .env
        echo -e "${YELLOW}⏭️  已跳过配置，请手动编辑 .env 文件${NC}"
        echo ""
        echo "📖 参考文档:"
        echo "   docs/MINIMAL_SETUP.md - 快速配置指南"
        echo "   docs/API_KEYS_EXPLAINED.md - API密钥详解"
        echo "   docs/LITELLM_INTEGRATION.md - LiteLLM 集成指南"
    fi
fi

echo ""

# 安装包（可选）
echo "📦 步骤 4/6: 安装命令行工具"
echo "------------------------------------------"

read -p "是否安装到系统? 安装后可使用 'legal-rights' 命令 (y/n，默认 y): " install_cmd

if [ -z "$install_cmd" ] || [ "$install_cmd" = "y" ] || [ "$install_cmd" = "Y" ]; then
    echo "正在安装..."
    pip3 install -e . --quiet
    echo -e "${GREEN}✅ 已安装命令: legal-rights${NC}"
    echo "   现在可以使用: legal-rights --help"
    INSTALLED_CMD=true
else
    echo "跳过安装，使用 'python3 -m legal_rights' 运行"
    INSTALLED_CMD=false
fi

echo ""

# 验证配置
echo "🔍 步骤 5/6: 验证配置"
echo "------------------------------------------"

if [ "$INSTALLED_CMD" = "true" ]; then
    legal-rights config
else
    python3 -m legal_rights config
fi

echo ""

# 构建知识库
echo "🏗️  步骤 6/6: 构建知识库"
echo "------------------------------------------"

read -p "是否现在构建知识库? 需要3-5分钟 (y/n，默认 y): " build_now

if [ -z "$build_now" ] || [ "$build_now" = "y" ] || [ "$build_now" = "Y" ]; then
    echo ""
    echo "开始构建知识库..."
    echo "这将从权威法律网站抓取内容并构建向量索引"
    echo ""
    echo -e "${YELLOW}💡 提示: 如果遇到网页抓取失败，属于正常现象（网站反爬虫）${NC}"
    echo "   可以稍后手动下载页面，详见: docs/SCRAPING_ISSUES.md"
    echo ""

    if [ "$INSTALLED_CMD" = "true" ]; then
        legal-rights build-kb || echo -e "${YELLOW}⚠️  知识库构建遇到问题，请查看上方错误信息${NC}"
    else
        python3 -m legal_rights build-kb || echo -e "${YELLOW}⚠️  知识库构建遇到问题，请查看上方错误信息${NC}"
    fi

    echo ""
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 知识库构建完成！${NC}"
    else
        echo -e "${YELLOW}⚠️  部分步骤失败，但可以继续使用${NC}"
        echo "   参考文档: docs/SCRAPING_ISSUES.md"
    fi
else
    echo "跳过构建，稍后可运行:"
    if [ "$INSTALLED_CMD" = "true" ]; then
        echo "  legal-rights build-kb"
    else
        echo "  python3 -m legal_rights build-kb"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 安装完成！${NC}"
echo "=========================================="
echo ""
echo "📚 快速开始:"
echo ""

if [ "$INSTALLED_CMD" = "true" ]; then
    echo "  # 单次问答"
    echo "  legal-rights ask \"公司恶意辞退不给补偿怎么办？\""
    echo ""
    echo "  # 交互式对话"
    echo "  legal-rights chat"
    echo ""
    echo "  # 查看配置"
    echo "  legal-rights config"
    echo ""
    echo "  # 查看帮助"
    echo "  legal-rights --help"
else
    echo "  # 单次问答"
    echo "  python3 -m legal_rights ask \"公司恶意辞退不给补偿怎么办？\""
    echo ""
    echo "  # 交互式对话"
    echo "  python3 -m legal_rights chat"
    echo ""
    echo "  # 查看配置"
    echo "  python3 -m legal_rights config"
    echo ""
    echo "  # 查看帮助"
    echo "  python3 -m legal_rights --help"
fi

echo ""
echo "📖 重要文档:"
echo "  ${BLUE}docs/MINIMAL_SETUP.md${NC} - 最简配置指南（推荐阅读）"
echo "  ${BLUE}docs/API_KEYS_EXPLAINED.md${NC} - API密钥详解"
echo "  ${BLUE}docs/MULTI_MODEL_SUPPORT.md${NC} - 多模型支持详解"
echo "  ${BLUE}docs/LITELLM_INTEGRATION.md${NC} - LiteLLM 集成指南（高级功能）"
echo "  ${BLUE}docs/FAQ.md${NC} - 常见问题"
echo "  ${BLUE}docs/SCRAPING_ISSUES.md${NC} - 网页抓取问题处理"
echo ""
echo "💡 提示:"
echo "  • 如果使用智谱AI，一个密钥可以完成所有功能"
echo "  • 如果使用 LiteLLM，可以统一管理所有模型（负载均衡、成本追踪）"
echo "  • 如果抓取失败，可以手动下载页面后添加到缓存"
echo "  • 运行 'config' 命令查看当前配置状态"
echo "  • 可以通过 LLM_MODE 环境变量随时切换模型"
echo ""
echo "🐛 遇到问题?"
echo "  1. 查看 docs/FAQ.md"
echo "  2. 查看 docs/API_KEYS_EXPLAINED.md"
echo "  3. 提交 Issue: https://github.com/YOUR_GITHUB_USERNAME/legal_rights/issues"
echo ""
