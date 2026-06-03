# 🦞 龙虾 AI 生产力播客

自动化播客系统：AI 搜集资讯 → 生成语音 → 自动发布到播客平台

## 📁 项目结构

```
lobster_podcast/
├── audio/              # 播客音频文件存放目录
├── scripts/            # 播客脚本存放目录
├── generate_feed.py    # RSS Feed 生成脚本
├── deploy.sh           # 自动部署脚本（生成RSS + Git推送）
├── daily_podcast.sh    # 每日播客生成脚本
├── feed.xml            # 自动生成的 RSS 文件
├── cover.png           # 播客封面图（可选）
└── README.md           # 本说明文件
```

## 🚀 一次性初始化

### 1. 创建 GitHub 仓库
```bash
# 在 GitHub 上创建公开仓库：lobster_podcast
# 然后关联本地仓库：
cd ~/lobster_podcast
git remote add origin git@github.com:tengjunqing/lobster_podcast.git
git branch -M master
git push -u origin master
```

### 2. 开启 GitHub Pages
- 进入 GitHub 仓库 → Settings → Pages
- Source 选择 `master` 分支
- 保存后会得到访问地址

### 3. 修改配置
编辑 `generate_feed.py` 中的 `BASE_URL` 为你的实际 GitHub Pages 地址

### 4. iPhone 订阅
1. 复制 RSS 地址：`https://tengjunqing.github.io/lobster_podcast/feed.xml`
2. 打开 iPhone「播客」App → 资料库 → 右上角 ··· → 通过 URL 添加播客
3. 粘贴链接，完成订阅

## 🤖 Agent 自动化流程

每天由 OpenClaw 定时任务自动执行以下流程：

```
1. 搜索当日 AI 资讯（Tavily）
2. 生成资讯摘要脚本
3. TTS 生成语音音频
4. 复制到 audio/ 目录
5. 运行 deploy.sh 自动发布
6. iPhone 播客 App 自动同步
```

### 音频命名规范
```
YYYYMMDD_时段_话题简称.mp3
```
示例：`20260603_Morning_AINews.mp3`

### 手动部署
```bash
cd ~/lobster_podcast
bash deploy.sh
```

## 📊 当前状态
- [x] 项目初始化
- [x] RSS 生成脚本
- [x] 部署脚本
- [x] GitHub 仓库创建并关联
- [x] GitHub Pages 开启
- [ ] iPhone 订阅
- [x] 定时任务配置
