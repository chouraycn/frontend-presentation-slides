# ⚡ 快速发布指南

## 📦 准备就绪

- ✅ 安装包: `dist/frontend-presentation-slides-v1.0.0.tar.gz` (344 KB)
- ✅ Git 标签: `v1.0.0`
- ✅ 文档完整
- ✅ 测试通过 (28/28)

---

## 🚀 平台 1: GitHub Releases

### 方法 1: 使用 GitHub CLI (gh) - 最快

```bash
# 1. 安装并登录 gh (如果还没有)
# macOS: brew install gh
gh auth login

# 2. 推送代码和标签
git push origin main
git push origin v1.0.0

# 3. 创建 Release
cd "/Users/chouray/Desktop/Front-end presentation slides"
gh release create v1.0.0 \
  dist/frontend-presentation-slides-v1.0.0.tar.gz \
  --title "Frontend Presentation Slides v1.0.0" \
  --notes "$(cat RELEASE_SUMMARY.md)"
```

### 方法 2: 使用 Web 界面

1. 推送代码:
   ```bash
   git push origin main
   git push origin v1.0.0
   ```

2. 访问: https://github.com/chouraycn/frontend-presentation-slides/releases/new

3. 填写:
   - Tag: `v1.0.0`
   - Title: `Frontend Presentation Slides v1.0.0`
   - Description: 复制 `RELEASE_SUMMARY.md` 内容

4. 上传: `dist/frontend-presentation-slides-v1.0.0.tar.gz`

5. 点击 "Publish release"

---

## 🎯 平台 2: WorkBuddy Marketplace

### 方法 1: 使用 CLI

```bash
# 1. 安装 CodeBuddy CLI
npm install -g @tencent-ai/codebuddy-code

# 2. 登录
codebuddy login

# 3. 发布
codebuddy publish:skill --path dist/frontend-presentation-slides-v1.0.0.tar.gz
```

### 方法 2: 使用 Web 界面

1. 访问 CodeBuddy Marketplace

2. 点击 "上传新 Skill"

3. 上传: `dist/frontend-presentation-slides-v1.0.0.tar.gz`

4. 填写信息:
   ```
   名称: Frontend Presentation Slides
   描述: Create zero-dependency, animation-rich HTML presentations
   分类: Productivity
   版本: 1.0.0
   标签: presentation, slides, html, animation, zero-dependency
   作者: chouray
   许可证: MIT
   仓库: https://github.com/chouraycn/frontend-presentation-slides
   ```

5. 点击 "发布"

---

## ✅ 完成！

发布后访问:
- GitHub: https://github.com/chouraycn/frontend-presentation-slides/releases/tag/v1.0.0
- WorkBuddy Marketplace: 查看你的 Skill 页面

---

## 📚 详细指南

查看完整文档: `RELEASE_INSTRUCTIONS.md`
