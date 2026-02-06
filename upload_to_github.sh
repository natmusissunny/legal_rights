#!/bin/bash

# 上传项目到 GitHub 的脚本
# GitHub 仓库: https://github.com/natmusissunny/legal_rights.git

set -e  # 遇到错误立即退出

echo "=========================================="
echo "📦 开始上传项目到 GitHub"
echo "=========================================="
echo ""

# 1. 检查是否已有 .git 目录
if [ -d ".git" ]; then
    echo "⚠️  检测到已存在的 Git 仓库"
    echo "是否要重新初始化? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        rm -rf .git
        echo "✅ 已删除旧的 Git 仓库"
    fi
fi

# 2. 初始化 Git 仓库
if [ ! -d ".git" ]; then
    echo "🔧 初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库初始化完成"
    echo ""
fi

# 3. 配置 Git 用户信息（如果未配置）
if [ -z "$(git config user.name)" ]; then
    echo "📝 请输入你的 Git 用户名:"
    read -r git_username
    git config user.name "$git_username"
fi

if [ -z "$(git config user.email)" ]; then
    echo "📝 请输入你的 Git 邮箱:"
    read -r git_email
    git config user.email "$git_email"
fi

echo "👤 Git 用户: $(git config user.name) <$(git config user.email)>"
echo ""

# 4. 添加所有文件
echo "📁 添加文件到 Git..."
git add .
echo "✅ 文件添加完成"
echo ""

# 5. 创建初始提交
echo "💾 创建提交..."
git commit -m "Initial commit: Legal Rights AI Assistant v1.0.2

- 完整的 RAG 架构实现
- 支持 Claude 4.5 和国内大模型（通义千问、智谱AI）
- FAISS 向量检索
- 完整的文档体系（11个专题文档）
- MIT 开源协议

Co-Authored-By: Claude Code <noreply@anthropic.com>"
echo "✅ 提交创建完成"
echo ""

# 6. 添加远程仓库
echo "🌐 配置远程仓库..."
REMOTE_URL="https://github.com/natmusissunny/legal_rights.git"

# 检查是否已有 origin
if git remote | grep -q "^origin$"; then
    echo "⚠️  已存在 origin 远程仓库，正在更新..."
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

echo "✅ 远程仓库配置完成: $REMOTE_URL"
echo ""

# 7. 重命名分支为 main（如果是 master）
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 重命名分支 $CURRENT_BRANCH 为 main..."
    git branch -M main
    echo "✅ 分支重命名完成"
    echo ""
fi

# 8. 推送到 GitHub
echo "🚀 推送到 GitHub..."
echo "⚠️  如果仓库已存在内容，可能需要使用 --force"
echo ""
echo "选择推送方式:"
echo "1) 正常推送 (git push -u origin main)"
echo "2) 强制推送 (git push -u origin main --force)"
echo ""
echo "请选择 (1 或 2):"
read -r push_choice

if [ "$push_choice" = "2" ]; then
    echo "⚠️  即将强制推送，这会覆盖远程仓库的内容"
    echo "确认继续? (y/n)"
    read -r confirm
    if [ "$confirm" = "y" ]; then
        git push -u origin main --force
    else
        echo "❌ 已取消推送"
        exit 1
    fi
else
    git push -u origin main
fi

echo ""
echo "=========================================="
echo "✅ 上传完成！"
echo "=========================================="
echo ""
echo "🎉 你的项目已经成功上传到:"
echo "📦 https://github.com/natmusissunny/legal_rights"
echo ""
echo "📋 下一步建议:"
echo "1. 访问仓库页面，添加 Topics 标签"
echo "2. 设置仓库描述"
echo "3. 创建 Release (v1.0.2)"
echo ""
echo "创建 Release 的命令:"
echo "gh release create v1.0.2 --title \"v1.0.2 - Initial Release\" --notes \"首次发布\""
echo ""
echo "或访问: https://github.com/natmusissunny/legal_rights/releases/new"
echo ""
