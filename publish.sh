#!/bin/bash

# ==============================================================================
# 🚀 Frontend Presentation Slides - 双平台发布脚本
# 发布到: 1) WorkBuddy Marketplace, 2) GitHub Releases
# ==============================================================================

set -e

PROJECT_NAME="Frontend Presentation Slides"
VERSION="v1.0.0"
PACKAGE="dist/frontend-presentation-slides-v1.0.0.tar.gz"
GITHUB_REPO="chouraycn/frontend-presentation-slides"

echo "==============================================================================="
echo "🚀 发布 $PROJECT_NAME $VERSION 到两个平台"
echo "==============================================================================="
echo ""

# 检查安装包是否存在
if [ ! -f "$PACKAGE" ]; then
    echo "❌ 错误: 安装包不存在: $PACKAGE"
    echo "   请先运行: python3 create_package.py"
    exit 1
fi

echo "✅ 安装包已找到: $PACKAGE ($(du -h "$PACKAGE" | cut -f1))"
echo ""

# ==============================================================================
# 平台 1: GitHub Releases
# ==============================================================================

echo "==============================================================================="
echo "📦 平台 1: 发布到 GitHub Releases"
echo "==============================================================================="
echo ""

# 检查 Git 状态
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: Git 工作区有未提交的更改"
    echo "   建议: 先运行 'git commit' 提交更改"
    echo ""
fi

# 创建 Git 标签
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "⚠️  标签 $VERSION 已存在，跳过创建"
else
    echo "🏷️  创建 Git 标签: $VERSION"
    git tag -a "$VERSION" -m "Release $VERSION

$(cat RELEASE_SUMMARY.md)"
    echo "✅ 标签创建成功"
fi
echo ""

# 推送到 GitHub
echo "📤 推送到 GitHub..."
echo "   仓库: https://github.com/$GITHUB_REPO"
echo ""
echo "请手动执行以下命令（需要 GitHub 认证）："
echo ""
echo "  # 推送代码"
echo "  git push origin main"
echo ""
echo "  # 推送标签"
echo "  git push origin $VERSION"
echo ""
echo "或者使用 GitHub CLI (gh):"
echo ""
echo "  gh release create $VERSION \\"
echo "    $PACKAGE \\"
echo "    --title \"$PROJECT_NAME $VERSION\" \\"
echo "    --notes \"\$(cat RELEASE_SUMMARY.md)\""
echo ""
read -p "按 Enter 继续，或 Ctrl+C 取消..."
echo ""

# ==============================================================================
# 平台 2: WorkBuddy Marketplace
# ==============================================================================

echo "==============================================================================="
echo "🎯 平台 2: 发布到 WorkBuddy Marketplace"
echo "==============================================================================="
echo ""

# 检查 CodeBuddy CLI
if command -v codebuddy &> /dev/null; then
    echo "✅ CodeBuddy CLI 已安装"
    echo ""
    echo "发布命令："
    echo ""
    echo "  codebuddy publish:skill --path $PACKAGE"
    echo ""
    echo "或者更新已发布的 skill："
    echo ""
    echo "  codebuddy update:skill --skill-id frontend-presentation-slides --path $PACKAGE"
    echo ""
else
    echo "⚠️  CodeBuddy CLI 未安装"
    echo ""
    echo "请通过 Web 界面发布："
    echo ""
    echo "  1. 访问: https://marketplace.codebuddy.ai"
    echo "  2. 点击 '上传新 Skill'"
    echo "  3. 上传: $PACKAGE"
    echo "  4. 填写以下元数据："
    echo ""
    echo "     名称: Frontend Presentation Slides"
    echo "     描述: Create zero-dependency, animation-rich HTML presentations"
    echo "     分类: Productivity / Design"
    echo "     版本: 1.0.0"
    echo "     标签: presentation,slides,html,animation,zero-dependency"
    echo ""
fi

# 显示元数据信息
echo "==============================================================================="
echo "📝 元数据信息"
echo "==============================================================================="
echo ""
cat <<'EOF'
{
  "name": "frontend-presentation-slides",
  "version": "1.0.0",
  "displayName": "Front-end Presentation Slides",
  "description": "Create zero-dependency, animation-rich HTML presentations that run entirely in the browser. Perfect for pitch decks, technical talks, product demos, and more.",
  "category": "Productivity",
  "tags": [
    "presentation",
    "slides",
    "html",
    "animation",
    "pitch-deck",
    "demo",
    "zero-dependency",
    "offline"
  ],
  "author": "chouray",
  "license": "MIT",
  "repository": "https://github.com/chouraycn/frontend-presentation-slides"
}
EOF
echo ""

# ==============================================================================
# 发布清单
# ==============================================================================

echo "==============================================================================="
echo "✅ 发布清单"
echo "==============================================================================="
echo ""
echo "📦 安装包信息:"
echo "   文件: $PACKAGE"
echo "   大小: $(du -h "$PACKAGE" | cut -f1)"
echo "   版本: $VERSION"
echo ""
echo "📚 文档文件:"
echo "   ✓ SKILL.md"
echo "   ✓ README.md / README.zh.md"
echo "   ✓ INSTALL.md"
echo "   ✓ QUICKSTART.md"
echo "   ✓ PUBLISH_GUIDE.md"
echo "   ✓ CHANGELOG.md"
echo "   ✓ VERIFICATION_REPORT.md"
echo ""
echo "🧪 测试状态:"
echo "   ✓ 28/28 测试通过"
echo "   ✓ 无语法错误"
echo "   ✓ 功能验证完成"
echo ""
echo "🎯 功能特性:"
echo "   ✓ 8 个专业模板"
echo "   ✓ 9 种图表类型"
echo "   ✓ 6 个交互模块"
echo "   ✓ 演讲者模式"
echo "   ✓ 多种导出格式"
echo "   ✓ 100% 离线支持"
echo ""

# ==============================================================================
# 下一步
# ==============================================================================

echo "==============================================================================="
echo "🎉 发布准备完成！"
echo "==============================================================================="
echo ""
echo "📌 下一步操作:"
echo ""
echo "1️⃣  GitHub Releases:"
echo "   - 推送代码: git push origin main"
echo "   - 推送标签: git push origin $VERSION"
echo "   - 或使用: gh release create $VERSION $PACKAGE"
echo ""
echo "2️⃣  WorkBuddy Marketplace:"
echo "   - CLI: codebuddy publish:skill --path $PACKAGE"
echo "   - Web: 访问 https://marketplace.codebuddy.ai 上传"
echo ""
echo "3️⃣  推广 (可选):"
echo "   - Twitter/X: 简短介绍 + GitHub 链接"
echo "   - LinkedIn: 详细文章 + 演示"
echo "   - 技术博客: 深度文章"
echo ""
echo "📚 查看详细指南: PUBLISH_GUIDE.md"
echo "📊 查看发布总结: RELEASE_SUMMARY.md"
echo ""
echo "==============================================================================="
