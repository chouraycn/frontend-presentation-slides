# 📤 发布指南

本指南帮助你将 `frontend-presentation-slides` 发布到不同的平台。

## 🎯 安装包信息

- **文件名**: `frontend-presentation-slides-v1.0.0.tar.gz`
- **位置**: `dist/frontend-presentation-slides-v1.0.0.tar.gz`
- **大小**: 350 KB (0.33 MB)
- **包含文件**: 57 个文件
- **版本**: v1.0.0

---

## 🌐 发布到 WorkBuddy Marketplace

### 方法 1: 使用 CodeBuddy CLI（推荐）

```bash
# 1. 登录到 CodeBuddy
codebuddy login

# 2. 发布到市场
codebuddy publish:skill --path dist/frontend-presentation-slides-v1.0.0.tar.gz

# 3. 如果需要更新已发布的 skill
codebuddy update:skill --skill-id frontend-presentation-slides --path dist/frontend-presentation-slides-v1.0.0.tar.gz
```

### 方法 2: 通过 Web 界面

1. 访问 [CodeBuddy Marketplace](https://marketplace.codebuddy.ai)
2. 点击"上传新 Skill"
3. 上传 `dist/frontend-presentation-slides-v1.0.0.tar.gz`
4. 填写元数据：
   - **名称**: Front-end Presentation Slides
   - **描述**: Create zero-dependency, animation-rich HTML presentations that run entirely in the browser
   - **分类**: Productivity / Design
   - **版本**: 1.0.0
   - **图标**: 上传一个图标（建议 256x256 PNG）
5. 发布

---

## 📦 发布到 GitHub Releases

### 1. 创建 GitHub 仓库（如果还没有）

```bash
# 初始化 git 仓库（如果还没有）
git init
git add .
git commit -m "Initial release v1.0.0"

# 创建 GitHub 仓库后，添加远程
git remote add origin https://github.com/YOUR_USERNAME/frontend-presentation-slides.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 2. 创建 GitHub Release

```bash
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0 - Initial release of Frontend Presentation Slides"

# 推送标签
git push origin v1.0.0

# 或者使用 GitHub CLI (gh)
gh release create v1.0.0 \
  dist/frontend-presentation-slides-v1.0.0.tar.gz \
  --title "Frontend Presentation Slides v1.0.0" \
  --notes "See RELEASE_SUMMARY.md for details"
```

### 3. 通过 GitHub Web 界面创建 Release

1. 访问你的 GitHub 仓库
2. 点击 "Releases" → "Draft a new release"
3. 填写信息：
   - **Tag**: `v1.0.0`
   - **Title**: `Frontend Presentation Slides v1.0.0`
   - **Description**: 复制 `RELEASE_SUMMARY.md` 的内容
4. 上传 `dist/frontend-presentation-slides-v1.0.0.tar.gz`
5. 点击 "Publish release"

---

## 🚀 发布到 npm（可选）

如果你想通过 npm 分发，可以创建一个 npm 包：

### 1. 创建 package.json

```bash
cd dist/frontend-presentation-slides
npm init -y
```

### 2. 编辑 package.json

```json
{
  "name": "frontend-presentation-slides",
  "version": "1.0.0",
  "description": "Create zero-dependency, animation-rich HTML presentations",
  "main": "index.js",
  "scripts": {
    "test": "python3 test_skill.py"
  },
  "keywords": [
    "presentation",
    "slides",
    "html",
    "animation",
    "zero-dependency"
  ],
  "author": "Your Name",
  "license": "MIT"
}
```

### 3. 发布到 npm

```bash
npm login
npm publish
```

---

## 📝 发布清单

发布前请确认以下事项：

### ✅ 必需文件

- [x] SKILL.md - Skill 定义文件
- [x] README.md - 项目说明
- [x] marketplace.json - 市场元数据
- [x] requirements.txt - 依赖清单
- [x] INSTALL.md - 安装指南
- [x] CHANGELOG.md - 版本历史
- [x] 所有脚本和模板文件

### ✅ 文档完整性

- [x] 中英文 README
- [x] 快速入门指南
- [x] 安装说明
- [x] 使用示例
- [x] 故障排除指南
- [x] 发布说明

### ✅ 测试状态

- [x] 所有测试通过 (28/28)
- [x] 无语法错误
- [x] 功能验证完成
- [x] 打包测试通过

### ✅ 版本信息

- [x] 版本号: v1.0.0
- [x] CHANGELOG 更新
- [x] Release Notes 准备好
- [x] 打包文件已创建

---

## 📊 元数据信息

### 用于 marketplace.json 或发布表单

```json
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
  "author": "Your Name",
  "license": "MIT",
  "repository": "https://github.com/YOUR_USERNAME/frontend-presentation-slides",
  "homepage": "https://github.com/YOUR_USERNAME/frontend-presentation-slides#readme",
  "icon": "assets/icon.png"
}
```

### 关键词（用于搜索优化）

- presentation, slides, slideshow, deck, pitch-deck
- html, css, javascript, animation
- zero-dependency, no-build, offline
- demo, showcase, portfolio
- tech-talk, investor, startup

---

## 🎯 发布后推广

### 1. 创建推广内容

- **Twitter/X**: 简短介绍 + GitHub 链接
- **LinkedIn**: 详细文章 + 演示视频
- **技术博客**: 深度文章
- **Product Hunt**: 产品发布

### 2. 推广文案模板

**Twitter/X**:
```
🎉 Just released Frontend Presentation Slides!

Create beautiful, animated HTML presentations with zero dependencies. 
Perfect for pitch decks, tech talks, and demos.

📦 Get it here: [链接]
#opensource #presentation #webdev
```

**LinkedIn**:
```
Excited to announce the release of Frontend Presentation Slides!

This open-source tool lets you create professional, animation-rich HTML presentations without any build tools or dependencies. Perfect for:

✅ Investor pitch decks
✅ Technical presentations  
✅ Product demos
✅ Design portfolios

Key features:
- 8 professional templates
- 9 chart types
- Speaker mode with dual windows
- Interactive modules (polls, quizzes, word clouds)
- Export to PDF/PPTX/MP4
- 100% offline capable

Check it out: [链接]

#opensource #webdev #presentation
```

---

## 🔗 有用的链接

- **项目主页**: `https://github.com/YOUR_USERNAME/frontend-presentation-slides`
- **文档**: `https://YOUR_USERNAME.github.io/frontend-presentation-slides`
- **问题追踪**: `https://github.com/YOUR_USERNAME/frontend-presentation-slides/issues`
- **更新日志**: `https://github.com/YOUR_USERNAME/frontend-presentation-slides/blob/main/CHANGELOG.md`

---

## 📞 获取帮助

如果发布过程中遇到问题：

1. 查看 `INSTALL.md` 安装指南
2. 查看 `references/TROUBLESHOOTING.md` 故障排除
3. 在 GitHub 上创建 issue
4. 联系 CodeBuddy 团队

---

## ✅ 下一步

1. ✅ 安装包已创建
2. ⏳ 选择发布平台
3. ⏳ 按照相应平台的说明发布
4. ⏣ 推广和分享

祝发布顺利！🚀
