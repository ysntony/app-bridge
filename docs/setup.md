# 安装与配置（iPhone-use 底座）

AppBridge 依赖 [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use) 作为与 iPhone 通信的底座。这份文档带你完成一次性配置。

## 前置条件清单

| 项 | 要求 | 说明 |
|---|---|---|
| macOS | 任意主流版本 | 运行本地 MCP server 与 Xcode |
| Xcode | **完整版**（App Store 安装） | 编译/签名/部署 WDA；**仅 Command Line Tools 不够** |
| Apple 账号 | 免费即可 | 给 WDA Runner 签名；免费账号 7 天后需重签 |
| iPhone | 任意较新机型 | USB 连 Mac、信任、开发者模式、解锁 |
| Python | 3.9+ | 运行 MCP server（仅用标准库） |
| Node.js | 20.19+ / 22.12+ / 24+ | USB 转发与屏幕流 |

## 安装步骤

### 1. 克隆并安装

```bash
git clone https://github.com/zhongerxin/iPhone-use
cd iPhone-use
sh scripts/install.sh
```

安装脚本会：
- 注册一个名为 `iphone_use` 的本地 MCP server
- 提示你**重连 Codex 聊天**以加载工具

### 2. Xcode 登录 Apple 账号并建证书

1. 打开 **Xcode → Settings... → Accounts**
2. 左下角 **+** → 登录你的 Apple ID
3. 选中账号 → **Manage Certificates...** → **+** 新增一个 **Apple Development** 证书

### 3. 获取 Team ID

Xcode 里不直接显示 Team ID，从钥匙串证书读：

```bash
security find-certificate -a -c "Apple Development" -p \
  | openssl x509 -noout -subject
```

输出里 `OU=XXXXXXXXXX` 的 10 位大写就是 Team ID。

### 4. 手机端准备

- **USB 连接并信任此 Mac**（手机弹出"要信任此电脑吗"点信任）
- **设置 → 隐私与安全性 → 开发者模式** 打开，按提示重启
- 保持**解锁**状态

### 5. 配置设备并构建 WDA

用 iPhone-use 的 setup 工具（在 MCP 客户端里调 `pua_setup`，或命令行）：

- `pua_setup action=configure` 填入 UDID、Team ID、bundle ID
- `pua_setup action=fetch` 拉取固定版本 WDA 源码
- `pua_setup action=build` 编译并部署到手机

构建成功后，手机会多出 **WebDriverAgentRunner** App。

### 6. 信任开发者证书（免费账号需要）

手机上：**设置 → 通用 → VPN与设备管理** → 找到你的 `Apple Development: xxx` → **信任**。

### 7. 启动 WDA 并验证

- `pua_setup action=start` 启动服务
- `pua_ready` 返回 `ready=true` 即就绪

## 免费账号的 7 天重签

免费 Apple 账号签的 WDA **7 天后过期**。到期后 `pua_setup action=start` 会失败，重新跑一遍 `pua_setup action=build` 重新签名即可（几秒）。付费开发者账号（$99/年）则一年一签。

## 常见问题

- **`devices: []`**：手机没识别到。确认 USB 连接、已信任、已解锁；iPhone Mirroring 会占用设备，先退出镜像。
- **构建报 `Developer Mode disabled`**：手机开发者模式没开，见第 4 步。
- **start 后 8100 连不上**：WDA App 没在前台跑，手机上手动点开 WebDriverAgentRunner 图标一次。
- **控件树返回空**：不是 App 不支持，是提取字段问题。查 `/source?format=json` 而非封装层结果，见 [accessibility.md](accessibility.md)。

## 关闭匿名统计（可选）

iPhone-use 默认向作者的 PostHog 发匿名使用统计（**不含画面/输入内容/设备标识**）。关闭：

```bash
export IPHONE_USE_ANALYTICS=0   # 或 DO_NOT_TRACK=1
# 重启 MCP server 生效
```
