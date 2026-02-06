#!/bin/bash

# 法律维权智能助手 - 一键安装脚本
# 适合小白用户快速部署

set -e

echo "=========================================="
echo "🚀 法律维权智能助手 - 一键安装"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

echo ""
echo -e "${YELLOW}🇨🇳 是否安装国内大模型支持? (推荐)${NC}"
echo "   安装后可使用通义千问和智谱AI（成本更低，速度更快）"
read -p "   安装? (y/n，默认 y): " install_domestic

if [ -z "$install_domestic" ] || [ "$install_domestic" = "y" ] || [ "$install_domestic" = "Y" ]; then
    echo "正在安装国内大模型支持..."
    pip3 install dashscope zhipuai --quiet
    echo -e "${GREEN}✅ 国内大模型支持已安装${NC}"
else
    echo "跳过国内大模型支持"
fi

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
    echo "请选择配置方案:"
    echo "  1) Claude + OpenAI (国际版)"
    echo "  2) 通义千问 + 智谱AI (国内版，推荐)"
    echo "  3) 跳过配置（稍后手动配置）"
    read -p "选择 (1/2/3，默认 2): " config_choice

    config_choice=${config_choice:-2}

    if [ "$config_choice" = "1" ]; then
        echo ""
        echo "配置 Claude + OpenAI:"
        read -p "  Claude API Key: " claude_key
        read -p "  OpenAI API Key: " openai_key

        cat > .env << EOF
# Claude API 配置（国际版）
CLAUDE_API_KEY=$claude_key
OPENAI_API_KEY=$openai_key

# LLM模式: auto, claude, qwen, zhipu
LLM_MODE=auto

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（Claude + OpenAI）${NC}"

    elif [ "$config_choice" = "2" ]; then
        echo ""
        echo "配置 通义千问 + 智谱AI:"
        echo ""
        echo "📌 如何获取 API 密钥:"
        echo "   通义千问: https://dashscope.console.aliyun.com/"
        echo "   智谱AI: https://open.bigmodel.cn/"
        echo ""
        read -p "  通义千问 API Key: " qwen_key
        read -p "  智谱AI API Key: " zhipu_key

        cat > .env << EOF
# 国内大模型配置（推荐）
DASHSCOPE_API_KEY=$qwen_key
ZHIPUAI_API_KEY=$zhipu_key

# LLM模式: auto, claude, qwen, zhipu
LLM_MODE=auto

# 速率限制（每秒请求数）
RATE_LIMIT_PER_SECOND=4
EOF
        echo -e "${GREEN}✅ .env 文件已创建（通义千问 + 智谱AI）${NC}"

    else
        cp .env.example .env
        echo -e "${YELLOW}⏭️  已跳过配置，请手动编辑 .env 文件${NC}"
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

    if [ "$INSTALLED_CMD" = "true" ]; then
        legal-rights build-kb
    else
        python3 -m legal_rights build-kb
    fi

    echo ""
    echo -e "${GREEN}✅ 知识库构建完成！${NC}"
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
    echo "  # 查看统计信息"
    echo "  legal-rights stats"
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
    echo "  # 查看统计信息"
    echo "  python3 -m legal_rights stats"
    echo ""
    echo "  # 查看帮助"
    echo "  python3 -m legal_rights --help"
fi

echo ""
echo "📖 文档:"
echo "  README.md - 项目介绍"
echo "  docs/SETUP_GUIDE.md - 详细配置指南"
echo "  docs/FAQ.md - 常见问题"
echo ""
echo "🐛 遇到问题?"
echo "  查看: docs/FAQ.md"
echo "  反馈: https://github.com/YOUR_GITHUB_USERNAME/legal_rights/issues"
echo ""
