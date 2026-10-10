#!/usr/bin/env python3
"""小红书：搜词 → 滚动 → 提取帖子 → 按互动排序。

直接调用 WDA 的 HTTP 接口（默认 http://127.0.0.1:18100），
用 /source?format=json 的 label 节点做结构化提取（不依赖截图 OCR）。

用法:
  python3 search_and_rank.py "GitHub 开源项目" [--screens 4] [--out result.json]

前提: WDA 已在 iPhone 上运行且 USB 转发已建立 (pua_ready == true)。
"""
import argparse, json, re, sys, time, urllib.request, urllib.parse

WDA = "http://127.0.0.1:18100"

def http(path, method="GET", body=None, timeout=20):
    url = WDA + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))

def wda_session():
    """建立/复用一个 WDA session 供动作接口调用。"""
    try:
        r = http("/session", "POST", {"capabilities": {"alwaysMatch": {"platformName": "iOS"}}})
        sid = r.get("sessionId") or (r.get("value") or {}).get("sessionId")
        return sid
    except Exception:
        return None

SID = wda_session()

def launch(bundle_id):
    if SID:
        try:
            http(f"/session/{SID}/url", "POST", {"url": f"{bundle_id}:"})
        except Exception:
            pass
    # 兜底：activate app
    try:
        http(f"/wda/apps/activate", "POST", {"bundleId": bundle_id})
    except Exception:
        pass

def tap(x, y):
    if SID:
        try:
            http(f"/session/{SID}/actions", "POST", {
                "actions": [{"type": "pointer", "id": "f", "parameters": {"pointerType": "touch"},
                             "actions": [{"type": "pointerMove", "duration": 0, "x": x, "y": y},
                                         {"type": "pointerDown", "button": 0},
                                         {"type": "pause", "duration": 60},
                                         {"type": "pointerUp", "button": 0}]}]})
            return
        except Exception:
            pass

def swipe_up():
    if SID:
        try:
            http(f"/session/{SID}/actions", "POST", {
                "actions": [{"type": "pointer", "id": "f", "parameters": {"pointerType": "touch"},
                             "actions": [{"type": "pointerMove", "duration": 0, "x": 201, "y": 620},
                                         {"type": "pointerDown", "button": 0},
                                         {"type": "pointerMove", "duration": 400, "x": 201, "y": 230},
                                         {"type": "pointerUp", "button": 0}]}]})
        except Exception:
            pass

def type_text(text):
    if SID:
        try:
            http(f"/session/{SID}/actions", "POST", {
                "actions": [{"type": "key", "id": "k",
                             "actions": [{"type": "keyDown", "value": c} for c in text] +
                                        [{"type": "keyUp", "value": c} for c in text]}]})
        except Exception:
            pass

def tree_nodes():
    """返回当前前台 App 的 (label, type, frame) 节点列表。"""
    raw = urllib.request.urlopen(WDA + "/source?format=json", timeout=15).read().decode("utf-8", "ignore")
    nodes = []
    for m in re.finditer(r'\{[^{}]*"type"\s*:\s*"(\w+)"[^{}]*"label"\s*:\s*"((?:[^"\\]|\\.)*)"[^{}]*"frame"\s*:\s*\{\{(\d+),\s*(\d+)\},\s*\{(\d+),\s*(\d+)\}\}[^{}]*\}', raw):
        t, label, x, y, w, h = m.group(1), m.group(2), *map(int, m.groups()[2:])
        nodes.append({"type": t, "label": label, "x": x, "y": y, "w": w, "h": h})
    # 更宽松的兜底：只抓 type+label
    if not nodes:
        for m in re.finditer(r'"type"\s*:\s*"(\w+)"[^{}]*?"label"\s*:\s*"((?:[^"\\]|\\.)*)"', raw):
            label = m.group(2).strip()
            if label:
                nodes.append({"type": m.group(1), "label": label})
    return nodes

def parse_posts(nodes):
    """从节点里解析帖子: 标题 + 作者 + 点赞数。小红书卡片底部通常是 作者名 + 数字(点赞)。"""
    texts = [n["label"] for n in nodes if n.get("label")]
    posts = []
    # 作者后面紧跟一个纯数字 → 视为 (作者, 点赞)
    for i, t in enumerate(texts):
        if re.fullmatch(r"\d{1,7}", t or ""):
            likes = int(t)
            author = texts[i-1] if i >= 1 else ""
            # 往前找最近的标题（作者之前的非数字、非栏目文本）
            title = ""
            for j in range(i-2, max(-1, i-6), -1):
                cand = texts[j]
                if cand and not re.fullmatch(r"\d+", cand) and cand not in ("关注","探索","附近","搜索","全部","用户","商品","图片","地点") and len(cand) > 4:
                    title = cand
                    break
            if likes >= 0 and (author or title):
                posts.append({"title": title, "author": author, "likes": likes})
    # 去重
    seen, out = set(), []
    for p in posts:
        k = (p["title"], p["author"])
        if k not in seen:
            seen.add(k); out.append(p)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword")
    ap.add_argument("--screens", type=int, default=4)
    ap.add_argument("--bundle", default="com.xingin.discover")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    launch(args.bundle); time.sleep(4)
    # 点搜索图标（小红书首页右上角放大镜，点坐标按 402x874 视口）
    tap(371, 85); time.sleep(1.5)
    # 点搜索框并输入
    tap(167, 85); time.sleep(0.6)
    type_text(args.keyword); time.sleep(0.8)
    # 点键盘搜索键
    tap(346, 778); time.sleep(3)

    all_posts = []
    for s in range(max(1, args.screens)):
        nodes = tree_nodes()
        all_posts.extend(parse_posts(nodes))
        if s < args.screens - 1:
            swipe_up(); time.sleep(2)

    # 去重 + 按点赞排序
    seen, uniq = set(), []
    for p in all_posts:
        k = (p["title"], p["author"])
        if k not in seen:
            seen.add(k); uniq.append(p)
    uniq.sort(key=lambda p: -p["likes"])

    result = {"keyword": args.keyword, "count": len(uniq), "posts": uniq}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w").write(out)
        print("已写入", args.out)
    print(out)

if __name__ == "__main__":
    main()
