# 小红书：舆情 / 竞品 / 内容采集

搜词 → 滚动信息流 → 提取帖子（标题/作者/点赞）→ 按互动排序。

## 用法

```bash
python3 search_and_rank.py "GitHub 开源项目" --screens 4 --out result.json
```

- `keyword`：搜索词（支持中文，WDA 原生 Unicode 注入，无拼音候选问题）
- `--screens`：滚动抓几屏（默认 4）
- `--out`：可选，结果写到 JSON 文件

## 前提

- WDA 在 iPhone 上运行、USB 转发已建立（`pua_ready == true`）
- 小红书已登录（你的真实账号）

## 提取逻辑

- 通过 WDA `/source?format=json` 拿控件树的 `label` 节点（**不用截图 OCR**，快且准）
- 卡片底部"作者名 + 数字"识别为（作者, 点赞）；向前回溯最近的非数字长文本作为标题
- 去重后按点赞数降序

## 典型场景

- **品牌舆情**：定时搜"Kimi K2"、"月之暗面"，抓新笔记做 sentiment 分析
- **竞品追踪**：搜"豆包"、"文心一言"、"通义千问"
- **KOL 发现**：搜关键词，按点赞/评论排序找高影响力博主
- **内容运营**：抓高热笔记，分析受欢迎的标题/封面/结构

## 输出示例

见 [../../examples/find-hot-github-posts.json](../../examples/find-hot-github-posts.json)。
