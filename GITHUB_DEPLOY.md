# GitHub Pages 部署指南

## 问题原因
之前 GitHub Pages 无法显示项目，是因为：
1. **缺少入口文件**：GitHub Pages 默认查找 `index.html` 作为首页
2. **中文文件名**：原文件 `京杭大运河_游客导览增强版_三次修改.html` 包含中文字符，可能导致路径问题

## 已解决的问题
✅ 已创建 `index.html` 文件，内容与原文件完全相同

## 如何部署到 GitHub Pages

### 步骤 1：上传文件到 GitHub
1. 确保你的仓库包含以下文件：
   - `index.html` (必须！)
   - 其他项目文件（可选）

2. 推送到 GitHub 仓库

### 步骤 2：启用 GitHub Pages
1. 进入你的 GitHub 仓库
2. 点击 **Settings**（设置）
3. 在左侧菜单找到 **Pages**（页面）
4. 在 **Build and deployment** 部分：
   - **Source** 选择：`Deploy from a branch`
   - **Branch** 选择：你的主分支（通常是 `main` 或 `master`）
   - **Folder** 选择：`/ (root)`
5. 点击 **Save**（保存）

### 步骤 3：等待部署
1. GitHub Pages 通常需要 1-5 分钟来部署
2. 部署完成后，在 Pages 设置页面可以看到访问链接
3. 访问格式：`https://你的用户名.github.io/你的仓库名/`

## 本地预览
在部署前，可以在本地预览：
- 直接在浏览器中打开 `index.html` 文件即可

## 注意事项
⚠️ **重要**：
1. 确保 `index.html` 在仓库根目录
2. 如果使用 GitHub Pages 的自定义域名，请在仓库设置中配置
3. 所有图片资源确保可以正常访问（本项目使用的是外部图片服务，无需额外配置）

## 部署后检查
✅ 访问链接是否正常显示
✅ 所有功能是否正常工作
✅ 图片是否正确加载

## 需要帮助？
如果部署遇到问题，可以：
1. 检查 GitHub Pages 的构建日志
2. 确保 `index.html` 存在且文件名正确
3. 确认仓库分支选择正确