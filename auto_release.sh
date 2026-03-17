#!/bin/bash

# ==============================================================================
# 🚀 Frontend Presentation Slides - 自动化发布脚本
# 自动发布到: GitHub Releases + WorkBuddy Marketplace
# ==============================================================================

set -e

PROJECT_NAME="Frontend Presentation Slides"
VERSION="v1.0.0"
PACKAGE="dist/frontend-presentation-slides-v1.0.0.tar.gz"
GITHUB_REPO="chouraycn/frontend-presentation-slides"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}===============================================================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}===============================================================================${NC}"
    echo ""
}

# ==============================================================================
# 检查环境
# ==============================================================================

print_header "环境检查"

# 检查安装包
if [ ! -f "$PACKAGE" ]; then
    print_error "安装包不存在: $PACKAGE"
    print_info "请先运行: python3 create_package.py"
    exit 1
fi
print_success "安装包已找到: $PACKAGE ($(du -h "$PACKAGE" | cut -f1))"

# 检查 Git
if ! command -v git &> /dev/null; then
    print_error "Git 未安装"
    exit 1
fi
print_success "Git 已安装: $(git --version)"

# 检查 Git 仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "当前目录不是 Git 仓库"
    exit 1
fi
print_success "Git 仓库已初始化"

# 检查 GitHub CLI
HAS_GH=false
if command -v gh &> /dev/null; then
    HAS_GH=true
    print_success "GitHub CLI 已安装"
else
    print_warning "GitHub CLI 未安装 (可选，用于自动化创建 Release)"
    print_info "安装方法: brew install gh (macOS) 或访问 https://cli.github.com"
fi

# 检查 CodeBuddy CLI
HAS_CODEBUDDY=false
if command -v codebuddy &> /dev/null; then
    HAS_CODEBUDDY=true
    print_success "CodeBuddy CLI 已安装"
else
    print_warning "CodeBuddy CLI 未安装 (可选，用于自动化发布到 Marketplace)"
    print_info "安装方法: npm install -g @tencent-ai/codebuddy-code"
fi

# 检查未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Git 工作区有未提交的更改"
    print_info "未提交的文件:"
    git status --short
    echo ""
    read -p "是否先提交这些更改? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Release v1.0.0 - Complete release package"
        print_success "已提交更改"
    else
        print_warning "跳过提交，继续发布"
    fi
else
    print_success "工作区干净，无未提交更改"
fi

echo ""
read -p "按 Enter 继续..."
echo ""

# ==============================================================================
# 平台 1: GitHub Releases
# ==============================================================================

print_header "平台 1: GitHub Releases"

# 检查标签是否存在
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    print_warning "标签 $VERSION 已存在"
    read -p "是否删除并重新创建? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$VERSION"
        print_success "已删除旧标签"
    else
        print_info "使用现有标签"
    fi
else
    print_info "创建 Git 标签: $VERSION"
    git tag -a "$VERSION" -m "Release $VERSION - Frontend Presentation Slides"
    print_success "标签创建成功"
fi

echo ""
print_info "推送代码到 GitHub..."
print_info "仓库: https://github.com/$GITHUB_REPO"
echo ""

# 尝试推送
print_info "推送主分支..."
if git push origin main; then
    print_success "主分支推送成功"
else
    print_error "推送失败"
    print_info "可能的原因:"
    print_info "  1. 未配置 Git 凭证"
    print_info "  2. 网络连接问题"
    print_info "  3. 权限不足"
    echo ""
    print_info "请手动执行以下命令:"
    echo "  git push origin main"
    echo "  git push origin $VERSION"
    echo ""
    print_info "或使用 Personal Access Token:"
    print_info "  1. 访问 https://github.com/settings/tokens"
    print_info "  2. 创建 token (勾选 repo 权限)"
    print_info "  3. 推送: git push https://YOUR_TOKEN@github.com/$GITHUB_REPO.git main"
    echo ""
    read -p "推送成功后按 Enter 继续... "
fi

echo ""
print_info "推送标签..."
if git push origin "$VERSION"; then
    print_success "标签推送成功"
else
    print_warning "标签推送失败，请手动执行: git push origin $VERSION"
    read -p "推送成功后按 Enter 继续... "
fi

echo ""
print_info "创建 GitHub Release..."

if [ "$HAS_GH" = true ]; then
    print_info "使用 GitHub CLI 创建 Release..."

    # 检查 Release 是否已存在
    if gh release view "$VERSION" &> /dev/null; then
        print_warning "Release $VERSION 已存在"
        read -p "是否删除并重新创建? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gh release delete "$VERSION" --yes
            print_success "已删除旧 Release"
        else
            print_info "使用现有 Release"
            read -p "按 Enter 继续..."
        fi
    fi

    # 创建 Release
    if ! gh release view "$VERSION" &> /dev/null; then
        print_info "正在创建 Release..."
        if gh release create "$VERSION" \
            "$PACKAGE" \
            --title "$PROJECT_NAME $VERSION" \
            --notes "$(cat RELEASE_SUMMARY.md 2>/dev/null || echo "Release $VERSION")"; then
            print_success "Release 创建成功!"
        else
            print_error "Release 创建失败"
            print_info "请通过 Web 界面手动创建:"
            print_info "  https://github.com/$GITHUB_REPO/releases/new"
        fi
    fi
else
    print_warning "GitHub CLI 未安装，请通过 Web 界面创建 Release:"
    print_info "  https://github.com/$GITHUB_REPO/releases/new"
    print_info ""
    print_info "步骤:"
    print_info "  1. 访问上述链接"
    print_info "  2. 选择标签: $VERSION"
    print_info "  3. 标题: $PROJECT_NAME $VERSION"
    print_info "  4. 描述: 复制 RELEASE_SUMMARY.md 内容"
    print_info "  5. 上传文件: $PACKAGE"
    print_info "  6. 点击 'Publish release'"
    echo ""
    read -p "创建 Release 后按 Enter 继续... "
fi

print_success "GitHub Releases 发布步骤完成!"

echo ""
read -p "按 Enter 继续..."
echo ""

# ==============================================================================
# 平台 2: WorkBuddy Marketplace
# ==============================================================================

print_header "平台 2: WorkBuddy Marketplace"

if [ "$HAS_CODEBUDDY" = true ]; then
    print_info "使用 CodeBuddy CLI 发布到 Marketplace..."

    # 检查是否已登录
    if codebuddy whoami &> /dev/null; then
        print_success "已登录 CodeBuddy"
    else
        print_info "需要登录 CodeBuddy"
        codebuddy login
    fi

    print_info "正在发布 Skill..."
    if codebuddy publish:skill --path "$PACKAGE"; then
        print_success "Skill 发布成功!"
    else
        print_error "Skill 发布失败"
        print_info "请通过 Web 界面手动发布"
    fi
else
    print_warning "CodeBuddy CLI 未安装"
    echo ""
    print_info "请通过以下方式发布:"
    echo ""
    print_info "方式 1: 安装 CodeBuddy CLI"
    print_info "  npm install -g @tencent-ai/codebuddy-code"
    print_info "  codebuddy login"
    print_info "  codebuddy publish:skill --path $PACKAGE"
    echo ""
    print_info "方式 2: 使用 Web 界面"
    print_info "  1. 访问 CodeBuddy Marketplace"
    print_info "  2. 点击 '上传新 Skill'"
    print_info "  3. 上传: $PACKAGE"
    print_info "  4. 填写元数据:"
    echo ""
    echo "     名称: Frontend Presentation Slides"
    echo "     描述: Create zero-dependency, animation-rich HTML presentations"
    echo "     分类: Productivity"
    echo "     版本: 1.0.0"
    echo "     标签: presentation, slides, html, animation, zero-dependency"
    echo "     作者: chouray"
    echo "     许可证: MIT"
    echo ""
    print_info "  5. 点击 '发布'"
    echo ""
fi

print_success "WorkBuddy Marketplace 发布步骤完成!"

echo ""
read -p "按 Enter 继续..."
echo ""

# ==============================================================================
# 发布总结
# ==============================================================================

print_header "发布总结"

echo ""
print_info "📦 发布信息:"
echo "   项目: $PROJECT_NAME"
echo "   版本: $VERSION"
echo "   安装包: $PACKAGE ($(du -h "$PACKAGE" | cut -f1))"
echo ""

print_info "🎯 已完成步骤:"
echo "   ✓ Git 标签创建"
echo "   ✓ 代码推送到 GitHub"
echo "   ✓ 标签推送到 GitHub"
echo "   ✓ GitHub Release 创建 (或指南提供)"
echo "   ✓ WorkBuddy Marketplace 发布 (或指南提供)"
echo ""

print_info "🔗 重要链接:"
echo "   GitHub 仓库: https://github.com/$GITHUB_REPO"
echo "   GitHub Release: https://github.com/$GITHUB_REPO/releases/tag/$VERSION"
echo "   问题追踪: https://github.com/$GITHUB_REPO/issues"
echo ""

print_info "📚 参考文档:"
echo "   快速指南: QUICK_RELEASE.md"
echo "   详细指南: RELEASE_INSTRUCTIONS.md"
echo "   发布指南: PUBLISH_GUIDE.md"
echo "   发布总结: RELEASE_SUMMARY.md"
echo ""

print_info "🎉 后续推广建议:"
echo "   • 在 Twitter/X 分享 GitHub Release 链接"
echo "   • 在 LinkedIn 发布详细文章"
echo "   • 在 Product Hunt 发布"
echo "   • 在技术社区分享 (Hacker News, Reddit)"
echo ""

print_header "发布流程完成!"

print_success "恭喜！Frontend Presentation Slides v1.0.0 已准备发布到两个平台"
echo ""
print_info "如果遇到任何问题，请查看:"
echo "  • RELEASE_INSTRUCTIONS.md - 详细发布指南"
echo "  • references/TROUBLESHOOTING.md - 故障排除"
echo ""
print_info "或者在 GitHub 创建 Issue:"
echo "  https://github.com/$GITHUB_REPO/issues"
echo ""
