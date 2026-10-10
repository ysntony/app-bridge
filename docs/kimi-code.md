# 在 Kimi Code 中使用 AppBridge

Kimi Code 原生带 MCP client（`~/.kimi-code/config.toml` 里有 `[mcp.client]`），**零改动直连** iPhone-use 的 MCP server。

## 注册 MCP server

编辑（或新建）`~/.kimi-code/mcp.json`，把 `iphone_use` 加进 `mcpServers`：

```json
{
  "mcpServers": {
    "iphone_use": {
      "command": "python3",
      "args": ["/绝对路径/server/iphone_use.py"],
      "startupTimeoutMs": 30000,
      "toolTimeoutMs": 120000
    }
  }
}
```

把 `args` 里的路径换成你本机 iPhone-use 的实际路径（安装后通常在 `~/.codex/plugins/cache/iphone-use-local/iphone-use/<版本>/server/iphone_use.py`）。

> 如果你之前装过其它 MCP server（比如 `mirroir`），保留它们，在 `mcpServers` 里并列加一项即可。

## 验证

重启 Kimi Code，然后用自然语言调用：

> 调用 iphone_use 的 pua_ready 工具，返回 ready 状态。

Kimi 会拉起这个 stdio server 并调用工具。之后就能直接下任务，例如：

> 用 iPhone Use 打开小红书，搜"Kimi K2"，把高赞笔记整理成表格。

## 与 Codex 共用

Codex 和 Kimi Code 用的是**同一个本地 MCP server**，不用分别维护。只要 iPhone-use 装好、WDA 在手机上运行，两个客户端都能连。
