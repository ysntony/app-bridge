# 在 Codex 中使用 AppBridge

Codex 通过**插件**机制加载 iPhone-use 提供的 MCP server。

## 安装

```bash
git clone https://github.com/zhongerxin/iPhone-use
cd iPhone-use && sh scripts/install.sh
```

`install.sh` 会调用 `codex plugin` 把 `iphone_use` 注册为一个本地 MCP server（stdio），并提示你**重连 Codex 聊天**。

## 验证

重连后，Codex 就能调用 19 个 `pua_*` 工具，例如：

> 用 iPhone Use 打开小红书，搜"GitHub 开源项目"，滚动 3 屏把高赞帖子整理出来。

Codex 会自动编排：`pua_launch_app` → `pua_type_text` → `pua_swipe` → `pua_observe`。

## 常用工具一览

| 工具 | 用途 |
|---|---|
| `pua_ready` / `pua_setup` | 就绪检查 / 设备配置与启停 |
| `pua_launch_app` | 按 bundle_id 启动 App |
| `pua_observe` | 控件树 / 截图 |
| `pua_find` | 按 label 等查询定位元素 |
| `pua_tap` / `pua_swipe` | 点击 / 滑动 |
| `pua_type_text` | Unicode 输入（**不经系统输入法，无拼音候选**） |
| `pua_press_button` | 主屏幕等 |
| `pua_batch` / `pua_collect_list` | 组合动作 / 列表采集 |
| `pua_screen` | 屏幕预览开关 |

> 提示：取控件树用于结构化提取时，优先直接查 WDA 的 `/source?format=json`（见 [accessibility.md](accessibility.md)），比 `pua_observe mode:tree` 更完整。
