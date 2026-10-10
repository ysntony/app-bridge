# AppBridge

*[中文版](README.md)*

---

AppBridge is an **in-app information-collection toolkit**. Built on [WebDriverAgent](https://github.com/appium/WebDriverAgent) (Apple's official XCTest automation framework), it exposes an iPhone's UI structure and interactions to any MCP-compatible AI client (Codex, Kimi Code, Claude Desktop, Cursor…) through a local [MCP](https://modelcontextprotocol.io) server — plus ready-to-use collection scripts for common scenarios.

## How it works

![AppBridge architecture](docs/architecture.png)

*[Interactive architecture diagram (zoomable / exportable)](docs/architecture.html)*

**Two extraction modes** (tree-first, per app):

1. **Accessibility tree (preferred)** — pull semantic elements (text, type, coordinates) from WDA's `/source?format=json` and extract structured data directly. Fast, accurate, zero model cost.
2. **Screenshot + vision model (fallback)** — for the rare app with no usable tree, fall back to high-res screenshots fed to a vision model for OCR. Still works, but slower and costlier.

> ⚠️ **Key implementation detail**: to decide "does this app have an accessibility tree", you must query WDA's raw `/source` — **do not trust a wrapper's filtered output**. On iOS, readable text usually lives in an element's `label` field, not `name` — filtering by `name` will wrongly report "no tree". See [docs/accessibility.md](docs/accessibility.md).

## Measured: accessibility trees in mainstream apps

| App | label nodes | Tree | Tier |
|---|---|---|---|
| Douyin | 74 | ✅ rich | content consumption — safe to collect |
| Weibo | 74 | ✅ rich | content consumption — safe to collect |
| Bilibili | 70 | ✅ rich | content consumption — safe to collect |
| Zhihu | 69 | ✅ rich | content consumption — safe to collect |
| Jihuanshe | 43 | ✅ rich | content consumption — safe to collect |
| WeChat | 43 | ✅ rich | content consumption — safe to collect |
| Xiaohongshu | 38 | ✅ rich | content consumption — safe to collect |

See [docs/app-tiers.md](docs/app-tiers.md) for the app tiering and risk-control notes.

## Quick start

### Prerequisites

- macOS + full **Xcode** (not just Command Line Tools)
- An **Apple Developer account** (a free one works, to sign WDA; free accounts must re-sign every 7 days)
- An **iPhone** connected over USB — trusted, Developer Mode on, unlocked

### 1. Install iPhone-use (the foundation)

```bash
git clone https://github.com/zhongerxin/iPhone-use
cd iPhone-use && sh scripts/install.sh
```

Follow the prompts to complete Xcode signing, WDA build, device trust and Developer Mode. See [docs/setup.md](docs/setup.md).

### 2. Connect your AI client

- **Codex**: see [docs/codex.md](docs/codex.md)
- **Kimi Code**: see [docs/kimi-code.md](docs/kimi-code.md) — register the `iphone_use` server in `~/.kimi-code/mcp.json`, zero code changes

### 3. Try a scenario

Example — find high-engagement "GitHub open-source project" notes on Xiaohongshu:

```bash
python3 scenarios/xiaohongshu/search_and_rank.py "GitHub 开源项目" --screens 4
```

Outputs posts ranked by likes as structured JSON. More in [scenarios/](scenarios/).

## Scenarios

| Scenario | Path | What it does |
|---|---|---|
| Xiaohongshu listening / competitor tracking | [scenarios/xiaohongshu/](scenarios/xiaohongshu/) | search → scroll → extract → rank by engagement |
| Generic "search → extract → rank" | [scenarios/generic/](scenarios/generic/) | cross-app collection flow |

## Compliance & boundaries

- Built on **WebDriverAgent / Apple's official XCTest**; reads only **public information visible to your own account on your own device**.
- **No** reverse engineering, jailbreak, or private protocols; does not bypass platform security.
- **Respect each platform's terms**: content-consumption apps (Xiaohongshu/Weibo/Bilibili/Zhihu) are safe to collect; **e-commerce apps (Taobao/JD) read-only, never touch transactions**; **financial apps (Alipay/banking) should not be automated**.
- Login, payment, SMS/face verification, and password changes are **sensitive actions — do them yourself on the phone**, never hand them to automation.

## Known limits & costs

- iPhone must be **USB-connected to the Mac** (no wireless)
- Requires full Xcode + an Apple Developer account to sign WDA (free accounts re-sign every 7 days)
- Real app interaction is bound by animations/loading, ~8s per page (still far faster than by hand)
- The phone is largely occupied by WDA in the foreground during a run

## Acknowledgements

- [WebDriverAgent](https://github.com/appium/WebDriverAgent) — iOS automation execution service
- [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use) — the local MCP server & setup guide (this project's foundation)

## License

MIT
