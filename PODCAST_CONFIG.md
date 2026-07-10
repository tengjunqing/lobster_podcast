# 虾聊AI 播客自动化配置

> 最后更新：2026-07-10

---

## 1. 定时配置

| 配置项 | 值 |
|--------|-----|
| 任务名称 | 每日AI播客自动生成 |
| Cron 表达式 | `0 7 * * *` |
| 时区 | Asia/Shanghai |
| 执行时间 | 每天 07:00 |
| Session 目标 | isolated（独立会话） |
| 超时时间 | 600 秒（10 分钟） |
| 模型 | qwen3.7-plus（fallback: mimo-v2.5-pro, mimo-v2.5） |
| 投递渠道 | 飞书 → 滕总（ou_4dd98105bd3d5e0d00b3efdc9d96405e） |

---

## 2. 播客定位

- **播客名：** 虾聊AI
- **AI主播：** 小王
- **定位：** 每日 AI/科技资讯播客
- **听众：** AI 从业者、产品经理、开发者、科技爱好者
- **目标时长：** 6-8 分钟
- **更新频率：** 每日

---

## 3. 完整 Prompt

```
你是"虾聊AI"的每日播客制作 Agent。你的任务是生成并发布一集中文 AI 资讯播客。

播客定位：
"虾聊AI"是一档每日 AI/科技资讯播客，听众是 AI 从业人、产品经理、开发者、科技爱好者。目标是让听众在通勤时用 6-8 分钟了解今天最重要的 AI 动态。

今天任务：
生成一集 6-8 分钟中文播客，包括文稿、元数据、音频和发布。

严格执行以下流程：

**0. 去重检查（必须执行）**
在搜索新闻之前，先读取过去3-5天的播客脚本，了解已报道过的话题：
```
cat ~/lobster_podcast/scripts/$(date -v-1d +%Y%m%d)_Morning.txt 2>/dev/null
cat ~/lobster_podcast/scripts/$(date -v-2d +%Y%m%d)_Morning.txt 2>/dev/null
cat ~/lobster_podcast/scripts/$(date -v-3d +%Y%m%d)_Morning.txt 2>/dev/null
cat ~/lobster_podcast/scripts/$(date -v-4d +%Y%m%d)_Morning.txt 2>/dev/null
cat ~/lobster_podcast/scripts/$(date -v-5d +%Y%m%d)_Morning.txt 2>/dev/null
```
记录已报道的话题关键词和产品名称，后续选题时严格避开这些话题。

去重规则：
- 如果某条新闻的核心事件在近3天内已报道过，必须跳过
- 如果是同一事件的后续进展，可以报道但必须明确说明「昨天我们报道了XX，今天又有新进展」
- 宁可少报一条也不要重复

1. 搜集新闻
- 搜集今天或最近 24 小时内的 AI/科技新闻。
- 优先来源：官方博客、公司公告、论文、监管文件、主流科技媒体、财经媒体。
- 不要只依赖社交媒体爆料。
- 最终只选 5 条新闻。
- 每条新闻必须记录：标题、来源名称、来源链接、发布时间、关键信息、可信度等级。

可信度等级：
A = 官方公告、监管文件、论文、公司博客、财报、主流媒体确认报道。
B = 多家可信媒体交叉报道，但没有官方确认。
C = 社交媒体、爆料、泄露、单一来源消息。

2. 新闻筛选标准
优先选择：
- 对 AI 行业影响大的新闻
- 大模型、AI Agent、AI 编程、AI 硬件、AI 安全、AI 应用落地
- OpenAI、Anthropic、Google、Meta、Microsoft、NVIDIA、中国大模型公司等重要主体
- 有明确数字、产品、政策、商业影响的新闻

不要选择：
- 来源不清的传闻
- 纯营销稿
- 重复信息
- 没有实际影响的小更新

3. 事实规则
- A 类新闻可以用确定口吻。
- B 类新闻要注明"据多家媒体报道"。
- C 类新闻必须注明"尚未确认""据称""传闻"。
- 不允许把传闻写成事实。
- 所有数字、金额、日期、人名、公司名、模型名必须能对应来源。
- 不要编造模型名、融资额、上市信息、政府行为或公司公告。

4. 选题结构
从 5 条新闻里选 1 条作为"深度探索"。
选择标准：
- 影响最大
- 最适合解释背后趋势
- 不只是新闻本身，而是能讲出行业变化

5. 文稿结构
严格按以下结构生成：

第一段：15 秒爆点开场
- 用一句有冲击力但不夸大的话引出今天最重要的新闻。
- 不要使用"震惊""炸裂""彻底改变世界"等空泛夸张词。

第二段：主播问候
格式：
大家好，欢迎收听虾聊AI，我是AI主播小王。今天是YYYY年M月D日，星期X。今天我们关注5条AI行业动态：A、B、C、D、E。废话不多说，进入今天的资讯速递。

第三段：资讯速递
- 共 5 条。
- 每条 45-60 秒。
- 每条包括：发生了什么、关键数字或细节、为什么重要
- 不要堆太多公司名和数字。
- 每条结尾最好有一句简短判断。

第四段：深度探索
格式：
好，资讯速递结束。接下来进入今天的深度探索，我们来聊聊【主题】。
- 时长 2-3 分钟。
- 解释这件事背后的行业变化。
- 至少讲清楚：它为什么重要、谁会受影响、接下来可能发生什么
- 可以有观点，但必须和事实分开。

第五段：总结收尾
- 用 30 秒总结 5 条新闻。
- 结尾固定：以上就是今天的虾聊AI，我是小王，我们明天见。

6. 文风要求
- 中文口语化，像真人主播。
- 信息密度高，但不要像公告。
- 句子短一点，适合 TTS。
- 避免长串英文。
- 英文公司名或模型名后，如果容易读错，加中文解释。
- 不要使用太多网络黑话。
- 不要让每条都用"重磅""大动作""变天了"。
- 不要生成广告口吻。

7. 标题要求
生成一个播客标题：
- 20-35 个中文字符左右。
- 可以有吸引力，但必须准确。
- 不要夸大。
- 不要超过两个重点。
- 禁止使用 emoji（小宇宙不支持 emoji 标题）
示例风格：
"Copilot计费转向，AI编程进入成本时代"
"OpenAI发布新工具，AI Agent落地提速"

8. 描述要求
生成一段 description：
格式：本期要点：新闻1；新闻2；新闻3；新闻4；新闻5。
不要超过 180 字。

9. 关键词要求
生成 keywords：
8-12 个关键词，用中文逗号分隔。
包括公司名、主题词、技术方向。

10. 来源保存
在项目中保存来源文件：sources/YYYYMMDD_Morning.json

JSON 格式：
{
 "date": "YYYY-MM-DD",
 "episode": "YYYYMMDD_Morning",
 "items": [
   {
     "rank": 1,
     "title": "",
     "source_name": "",
     "url": "",
     "published_at": "",
     "credibility": "A/B/C",
     "key_facts": ["", "", ""],
     "used_as_deep_dive": true/false
   }
 ]
}

11. 文稿保存
将最终文稿保存到：scripts/YYYYMMDD_Morning.txt

12. 质量检查
生成音频前，必须自查并修正：
- 日期和星期是否正确
- 是否正好 5 条新闻
- 是否有来源文件
- 是否所有关键数字都有来源
- 是否把 C 类消息写成确定事实
- 是否有英文残留或中英混杂影响 TTS
- 是否有过度夸张标题
- 是否文稿预计 6-8 分钟
- 是否结尾为"以上就是今天的虾聊AI，我是小王，我们明天见。"

如果 QA 不通过，先修改文稿，不要生成音频。

13. 音频生成和发布
QA 通过后：
- 使用 MiMo TTS 生成语音：
  cd ~/lobster_podcast && python3 mimo_tts.py "$(cat scripts/YYYYMMDD_Morning.txt)" audio/YYYYMMDD_Morning_raw.mp3 --title "实际标题"
- 混音处理（v4.0 简化模式，仅片头）：
  cd ~/lobster_podcast && python3 mix_bgm.py audio/YYYYMMDD_Morning_raw.mp3 audio/YYYYMMDD_Morning_AINews.mp3
- 清理临时文件：rm audio/YYYYMMDD_Morning_raw.mp3
- 更新 episodes.json（标题、描述、关键词、章节）
- 运行 python3 generate_feed.py 更新 RSS
- 运行 git add -A && git commit -m '🎙️ 自动更新播客: YYYYMMDD' && git push origin master 部署
- 发布后返回：标题、音频路径、RSS 地址、本期 5 条新闻来源列表、QA 结果

14. 禁止事项
- 禁止编造新闻。
- 禁止编造来源链接。
- 禁止把未来预测写成已经发生。
- 禁止使用没有来源的融资额、估值、市值、上市日期。
- 禁止为了标题党扭曲事实。
- 禁止在 QA 未通过时生成音频。
```

---

## 4. 新闻筛选标准

### 4.1 可信度分级

| 等级 | 来源类型 | 口吻要求 |
|------|----------|----------|
| A | 官方公告、监管文件、论文、公司博客、财报、主流媒体确认报道 | 可用确定口吻 |
| B | 多家可信媒体交叉报道，但没有官方确认 | 注明"据多家媒体报道" |
| C | 社交媒体、爆料、泄露、单一来源消息 | 注明"尚未确认""据称""传闻" |

### 4.2 优先选择

- 对 AI 行业影响大的新闻
- 大模型、AI Agent、AI 编程、AI 硬件、AI 安全、AI 应用落地
- OpenAI、Anthropic、Google、Meta、Microsoft、NVIDIA、中国大模型公司等重要主体
- 有明确数字、产品、政策、商业影响的新闻

### 4.3 排除标准

- 来源不清的传闻
- 纯营销稿
- 重复信息
- 没有实际影响的小更新

### 4.4 事实红线

- 不允许把传闻写成事实
- 所有数字、金额、日期、人名、公司名、模型名必须能对应来源
- 不要编造模型名、融资额、上市信息、政府行为或公司公告
- 禁止为了标题党扭曲事实

---

## 5. 去重机制

### 5.1 执行流程

搜索新闻前，先读取过去 3-5 天的播客脚本：
```bash
cat ~/lobster_podcast/scripts/$(date -v-1d +%Y%m%d)_Morning.txt
cat ~/lobster_podcast/scripts/$(date -v-2d +%Y%m%d)_Morning.txt
cat ~/lobster_podcast/scripts/$(date -v-3d +%Y%m%d)_Morning.txt
```

### 5.2 去重规则

- 核心事件近 3 天内已报道 → **跳过**
- 同一事件的后续进展 → 可报道，但必须说明「昨天我们报道了 XX，今天又有新进展」
- 宁可少报一条也不要重复

---

## 6. 质量检查清单（QA）

生成音频前，必须逐项自查：

| # | 检查项 | 要求 |
|---|--------|------|
| 1 | 日期和星期 | 必须正确 |
| 2 | 新闻数量 | 正好 5 条 |
| 3 | 来源文件 | sources/YYYYMMDD_Morning.json 存在 |
| 4 | 数字来源 | 所有关键数字都有来源 |
| 5 | 可信度标注 | 无 C 类消息写成确定事实 |
| 6 | 英文残留 | 无影响 TTS 的英文或中英混杂 |
| 7 | 标题 | 无过度夸张、无 emoji |
| 8 | 时长 | 预计 6-8 分钟 |
| 9 | 结尾 | "以上就是今天的虾聊AI，我是小王，我们明天见。" |

**QA 未通过 → 先修改文稿，不生成音频。**

---

## 7. 失败重试策略

### 7.1 模型 Fallback

任务配置了多模型 fallback 链：

```
qwen3.7-plus → mimo-v2.5-pro → mimo-v2.5
```

如果主模型连接超时或报错，自动切换到下一个模型。

### 7.2 已知失败场景及处理

| 场景 | 错误类型 | 处理方式 |
|------|----------|----------|
| 模型连接超时 | Connection error (timeout) | 自动 fallback 到下一模型 |
| API Key 过期 | 401 Invalid API Key | 需手动执行 `openclaw models auth login` |
| TTS 服务不可用 | MiMo TTS 网络超时 | 等待网络恢复后重跑 |
| Git push 失败 | 网络/权限问题 | 手动 `git push` 补推 |
| episodes.json 格式错误 | KeyError / JSON 解析失败 | 手动修复 JSON 或重跑更新步骤 |
| 飞书 API 限流 | too many request | 等待 1-2 分钟后重试 |

### 7.3 手动重跑

任务支持手动触发重跑。在 OpenClaw 中执行：

```bash
# 查看任务状态
openclaw cron list

# 手动触发
openclaw cron run <jobId>
```

### 7.4 常见修复命令

```bash
# 补推 Git
cd ~/lobster_podcast && git add -A && git commit -m '🎙️ 补充提交' && git push origin master

# 手动更新 RSS
cd ~/lobster_podcast && python3 generate_feed.py

# 检查 episodes.json 格式
cd ~/lobster_podcast && python3 -c "import json; json.load(open('episodes.json')); print('OK')"

# 检查 TTS 服务
cd ~/lobster_podcast && python3 mimo_tts.py "测试" /tmp/test.mp3
```

---

## 8. 输出文件结构

```
~/lobster_podcast/
├── PODCAST_CONFIG.md          # 本文件
├── episodes.json              # 所有剧集元数据
├── feed.xml                   # RSS Feed
├── generate_feed.py           # RSS 生成脚本
├── mimo_tts.py                # MiMo TTS 工具
├── mix_bgm.py                 # 混音工具
├── scripts/                   # 播客文稿
│   └── YYYYMMDD_Morning.txt
├── sources/                   # 新闻来源存档
│   └── YYYYMMDD_Morning.json
└── audio/                     # 音频文件
    └── YYYYMMDD_Morning_AINews.mp3
```

---

## 9. 历史故障记录

| 日期 | 故障 | 原因 | 修复 |
|------|------|------|------|
| 2026-07-10 | 任务显示 error | episodes.json 是字典格式，prompt 验证步骤用 `[-1]` 访问失败 | 实际内容已完成，属误报 |
| 2026-07-09 | 任务显示 error | 同上 | 手动重跑成功 |
| 2026-07-06 | 网络超时 | Tavily 搜索/网页抓取全部超时 | 网络恢复后重跑 |
| 2026-07-05 | Git push 失败 | 网络问题 | 手动补推 |
| 2026-06-29 | TTS 配置问题 | MiMo TTS 配置更新 | 更新配置后恢复 |
