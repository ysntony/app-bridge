---
name: appbridge
description: |
  AppBridge lets AI read and operate real iPhone apps over USB — read app content (Xiaohongshu, WeChat, Douyin, Weibo, Bilibili, Zhihu) that has no public API and can't be scraped via web. Use when the user wants to monitor social media, track competitors, collect posts, search an app for content, or read information that only exists inside a mobile app. Built on WebDriverAgent (Apple's official XCTest) — compliant and low-risk. Requires an iPhone connected by USB with WDA running.
---

# AppBridge

Read and operate real iPhone apps over USB to access **App-only information** (no public API, web scraping gets blocked).

## When to use

- 监控社媒舆情（小红书/微博/抖音/B站/知乎 上的品牌/竞品讨论）
- 采集 App 内的帖子、文章、评论、榜单
- 在 App 里搜索内容并按互动量排序
- 读取只存在于 App、不开放 API 的信息

## Architecture

`AI → MCP (stdio) → iPhone-use (local server) → WebDriverAgent → iOS XCTest`

Two extraction modes, **accessibility-tree first**:
1. **控件树直读 (首选)** — WDA `/source?format=json`, parse `label` nodes. Fast, precise, zero model cost.
2. **截图 + 视觉模型 (兜底)** — only for apps with no usable tree.

## Critical: get the accessibility tree correctly

判断/提取控件树，**必须查 WDA 原生 `/source?format=json`，不要用会按 `name` 过滤的封装结果**。iOS 上可读文本在元素的 `label` 字段，`name` 多为 null——按 `name` 过滤会误报为"无控件树"。主流 App（抖音74/微博74/B站70/知乎69/微信43/小红书38）全都有丰富控件树。

## Core tools (MCP `iphone_use`)

| Tool | Use |
|---|---|
| `pua_ready` / `pua_setup` | 就绪检查 / 设备配置与启停 |
| `pua_launch_app` | 按 bundle_id 启动 App |
| `pua_observe` | 控件树 / 截图 |
| `pua_find` | 按 label 定位元素 |
| `pua_tap` / `pua_swipe` | 点击 / 滑动 |
| `pua_type_text` | Unicode 输入（不经系统输入法，无拼音候选） |
| `pua_batch` / `pua_collect_list` | 组合动作 / 列表采集 |

## Common bundle IDs

- 小红书 `com.xingin.discover`
- 微信 `com.tencent.xinWeChat`
- 抖音 `com.ss.iphone.ugc.Aweme`
- 微博 `com.sina.weibo`
- B站 `tv.danmaku.bilianime`
- 知乎 `com.zhihu.ios`
- 淘宝 `com.taobao.taobao4iphone`（⚠️ 只读，实测自动化触发风控登出）

## App tiers（务必遵守）

- 🟢 内容消费类（小红书/微博/B站/知乎/公众号）：放心采集
- 🟡 电商交易类（淘宝/京东）：**只读，不碰交易**；登录由用户手动完成
- 🔴 金融支付类（支付宝/银行 App）：**不要自动化**

**敏感操作（登录/支付/验证码/改密码）一律让用户在手机上手动完成**，不要替用户操作。

## Example: 小红书找高互动笔记

```
pua_launch_app com.xingin.discover
pua_tap (搜索图标) → pua_type_text "GitHub 开源项目" → pua_tap (搜索键)
循环: pua_swipe up → 取 /source?format=json 解析 label 节点
提取 标题/作者/点赞 → 去重 → 按点赞排序
```

参考实现：`scenarios/xiaohongshu/search_and_rank.py`。

## Prerequisites

- iPhone USB 连 Mac、信任、开发者模式、解锁
- WDA 已构建并信任（免费账号 7 天需重签）
- 目标 App 已登录（用真实账号）
