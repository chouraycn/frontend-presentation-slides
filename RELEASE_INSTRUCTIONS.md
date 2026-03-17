# 🚀 双平台发布指南

本指南帮助你将 `Frontend Presentation Slides` 发布到：
1. **GitHub Releases** (开源发布)
2. **WorkBuddy Marketplace** (CodeBuddy 生态)

---

## 📋 发布前检查

✅ **已完成:**
- 安装包已创建: `dist/frontend-presentation-slides-v1.0.0.tar.gz` (344 KB)
- Git 标签已创建: `v1.0.0`
- 所有文档已准备好
- 测试全部通过 (28/28)

---

## 📦 平台 1: GitHub Releases

### 方式 A: 使用命令行（推荐）

#### 步骤 1: 推送代码到 GitHub

```bash
cd "/Users/chouray/Desktop/Front-end presentation slides"

# 推送主分支
git push origin main

# 推送标签
git push origin v1.0.0
```

**如果遇到认证错误，请使用以下方法之一：**

**方法 1: 使用 Personal Access Token**
1. 访问 https://github.com/settings/tokens
2. 生成新的 token (勾选 `repo` 权限)
3. 使用 token 代替密码推送:
   ```bash
   git push https://YOUR_TOKEN@github.com/chouraycn/frontend-presentation-slides.git main
   git push https://YOUR_TOKEN@github.com/chouraycn/frontend-presentation-slides.git v1.0.0
   ```

**方法 2: 使用 SSH**
```bash
# 如果你有 SSH 密钥配置
git remote set-url origin git@github.com:chouraycn/frontend-presentation-slides.git
git push origin main
git push origin v1.0.0
```

#### 步骤 2: 创建 GitHub Release

**选项 1: 使用 GitHub CLI (gh) - 最简单**

```bash
# 安装 GitHub CLI (如果还没有)
# macOS: brew install gh
# 或访问: https://cli.github.com

# 登录
gh auth login

# 创建 Release
gh release create v1.0.0 \
  dist/frontend-presentation-slides-v1.0.0.tar.gz \
  --title "Frontend Presentation Slides v1.0.0" \
  --notes "$(cat RELEASE_SUMMARY.md)"
```

**选项 2: 使用 Web 界面**

1. 访问: https://github.com/chouraycn/frontend-presentation-slides/releases/new
2. 选择标签: `v1.0.0`
3. 标题: `Frontend Presentation Slides v1.0.0`
4. 描述: 复制 `RELEASE_SUMMARY.md` 的内容
5. 上传文件: `dist/frontend-presentation-slides-v1.0.0.tar.gz`
6. 点击 "Publish release"

---

## 🎯 平台 2: WorkBuddy Marketplace

### 方式 A: 使用 CodeBuddy CLI

```bash
# 安装 CodeBuddy CLI (如果还没有)
npm install -g @tencent-ai/codebuddy-code

# 登录到 CodeBuddy
codebuddy login

# 发布到市场
codebuddy publish:skill --path dist/frontend-presentation-slides-v1.0.0.tar.gz
```

### 方式 B: 使用 Web 界面

1. 访问 CodeBuddy Marketplace
   - 如果你有内部访问链接，请使用该链接
   - 或者在 CodeBuddy IDE 中打开 Marketplace

2. 点击 "上传新 Skill" 或 "Create New Skill"

3. 上传文件
   - 选择: `dist/frontend-presentation-slides-v1.0.0.tar.gz`
   - 上传后会自动解压并识别

4. 填写元数据

```
基本信息:
- 名称: Frontend Presentation Slides
- 显示名称: Front-end Presentation Slides
- 版本: 1.0.0
- 分类: Productivity (生产力) 或 Design (设计)

描述:
Create zero-dependency, animation-rich HTML presentations that run entirely in the browser. Perfect for pitch decks, technical talks, product demos, design portfolios, and more.

标签:
presentation, slides, html, animation, pitch-deck, demo, zero-dependency, offline, web-design

作者: chouray
许可证: MIT

仓库: https://github.com/chouraycn/frontend-presentation-slides
```

5. 上传图标 (可选但推荐)
   - 建议尺寸: 256x256 或 512x512 PNG
   - 可以使用项目中的 logo 或创建一个简单的图标

6. 预览和发布
   - 检查所有信息是否正确
   - 点击 "发布" 或 "Publish"

---

## 📝 发布清单

### GitHub Releases 检查清单

- [ ] 代码已推送到 main 分支
- [ ] 标签 v1.0.0 已推送
- [ ] Release 已创建
- [ ] 安装包已上传 (344 KB)
- [ ] Release Notes 已填写
- [ ] 仓库设置为 Public (如果想要公开访问)

### WorkBuddy Marketplace 检查清单

- [ ] 安装包已上传
- [ ] 所有元数据已填写
- [ ] 描述清晰完整
- [ ] 标签添加完毕
- [ ] 图标已上传（可选）
- [ ] 预览效果正常
- [ ] 已发布到市场

---

## 🎉 发布后推广

### 1. 创建推广文案

**Twitter/X (280 字符以内):**
```
🎉 刚发布了 Frontend Presentation Slides v1.0.0!

零依赖 HTML 幻灯片工具，支持动画、图表、演讲者模式
适合路演、技术演讲、产品演示

📦 GitHub: https://github.com/chouraycn/frontend-presentation-slides

#opensource #presentation #webdev #slides
```

**LinkedIn:**
```
🚀 Excited to announce the release of Frontend Presentation Slides v1.0.0!

这是一个零依赖的 HTML 幻灯片工具，可以创建专业、动画丰富的演示文稿。

✨ 主要特性:
• 8 个专业模板
• 9 种图表类型（零依赖 SVG）
• 6 个交互模块
• 演讲者模式（双窗口同步）
• 导出 PDF/PPTX/MP4
• 100% 离线支持

🎯 适用场景:
- 投资者路演 (Pitch Deck)
- 技术演讲
- 产品演示
- 设计作品集
- 业务汇报
- 开源项目介绍

📦 GitHub: https://github.com/chouraycn/frontend-presentation-slides
📚 文档: https://github.com/chouraycn/frontend-presentation-slides/blob/main/README.md

#opensource #webdev #presentation #slides #html #javascript
```

**技术博客标题:**
- "How to Create Professional Presentations Without Build Tools"
- "Building Zero-Dependency HTML Slides with Native JavaScript"
- "Frontend Presentation Slides: A Modern Approach to Web Presentations"

### 2. 提交到目录

- **Product Hunt**: https://www.producthunt.com/posts/new
- **Hacker News**: https://news.ycombinator.com/newest
- **Reddit**: r/opensource, r/webdev, r/javascript
- **Awesome Lists**: 提交到相关的 awesome 列表

### 3. 创建演示

创建一个在线演示链接：
- GitHub Pages: https://chouraycn.github.io/frontend-presentation-slides/
- Vercel/Netlify: 部署 assets/demos/ 目录

---

## 📊 发布统计

发布完成后，记录以下数据：

### GitHub Analytics
- [ ] Stars ⭐
- [ ] Forks 🍴
- [ ] Release 下载次数 📥
- [ ] Clone 次数 📊
- [ ] Views 👁️

### WorkBuddy Marketplace
- [ ] 安装次数
- [ ] 评分 ⭐
- [ ] 评论数量
- [ ] 使用频率

---

## 🔗 有用链接

- **GitHub 仓库**: https://github.com/chouraycn/frontend-presentation-slides
- **Release 页面**: https://github.com/chouraycn/frontend-presentation-slides/releases/tag/v1.0.0
- **Issues**: https://github.com/chouraycn/frontend-presentation-slides/issues
- **Wiki**: https://github.com/chouraycn/frontend-presentation-slides/wiki

---

## 🐛 发布后监控

发布后密切关注：

1. **Issue 追踪**: 检查是否有 bug 报告
2. **Pull Requests**: 接受社区贡献
3. **用户反馈**: 收集使用体验和建议
4. **性能监控**: 如果有在线版本，监控加载速度
5. **文档改进**: 根据用户问题改进文档

---

## 🔄 下一步版本

发布后，开始规划 v1.1.0：

### 可能的新特性
- [ ] 更多模板
- [ ] 更多图表类型
- [ ] 更多交互模块
- [ ] 国际化支持
- [ ] 主题编辑器
- [ ] 云端保存
- [ ] 协作功能

### Bug 修复
- [ ] 收集并修复用户报告的问题
- [ ] 性能优化
- [ ] 兼容性改进

---

## 📞 获取帮助

如果发布过程中遇到问题：

1. **查看文档**: `PUBLISH_GUIDE.md`, `INSTALL.md`
2. **GitHub Issues**: 在仓库创建 issue
3. **联系 CodeBuddy 团队**: 通过内部渠道

---

## ✅ 快速命令参考

```bash
# Git 相关
git status                              # 检查状态
git add .                              # 添加所有更改
git commit -m "message"                # 提交
git push origin main                   # 推送主分支
git tag -a v1.0.0 -m "message"          # 创建标签
git push origin v1.0.0                 # 推送标签

# GitHub CLI
gh auth login                          # 登录
gh release create v1.0.0 <file>        # 创建 Release
gh repo view                           # 查看仓库

# CodeBuddy
codebuddy login                         # 登录
codebuddy publish:skill --path <file>  # 发布 Skill

# 本地测试
python3 test_skill.py                  # 运行测试
python3 create_package.py              # 创建安装包
```

---

## 🎉 祝发布成功！

期待看到你的 Frontend Presentation Slides 在两个平台上获得成功！

有任何问题，随时创建 GitHub Issue 或联系我。

---

*发布日期: 2026-03-17*
*版本: v1.0.0*
