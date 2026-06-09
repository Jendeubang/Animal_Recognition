"""
动物图片下载工具（DuckDuckGo 图片搜索）
用法: python download_images.py
"""

import os
import urllib.request
import urllib.parse
import json
import time
import re
import ssl
import sys

# 绕过系统代理
proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)
ssl._create_default_https_context = ssl._create_unverified_context

# ── 配置 ──
NEW_CLASSES = [
    ("uccello",   "鸟",   "bird"),
    ("anatra",    "鸭子",  "duck"),
    ("coniglio",  "兔子",  "rabbit"),
    ("tigre",     "老虎",  "tiger"),
    ("leone",     "狮子",  "lion"),
    ("scimmia",   "猴子",  "monkey"),
]

TARGET_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-img")
IMAGES_PER_CLASS = 100


def search_images_ddg(query, max_results=150):
    """从 DuckDuckGo 图片搜索获取图片 URL"""
    urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, */*',
        'Referer': 'https://duckduckgo.com/',
    }

    # 先获取 vqd 参数
    search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query + ' animal photo')}&t=h_&iax=images&ia=images"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # 提取 vqd
        vqd_match = re.search(r'vqd=([\d-]+)', html)
        if not vqd_match:
            print("    无法获取 vqd 参数")
            return []
        vqd = vqd_match.group(1)
    except Exception as e:
        print(f"    获取 vqd 失败: {e}")
        return []

    # 用 vqd 请求图片 API
    api_url = f"https://duckduckgo.com/i.js?q={urllib.parse.quote(query + ' animal photo')}&vqd={vqd}&o=json&p=1&f=,,,&l=us-en"
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        for item in data.get('results', []):
            url = item.get('image', '')
            if url and url.startswith('http'):
                urls.append(url)
    except Exception as e:
        print(f"    API 请求失败: {e}")

    return urls


def download_image(url, save_path):
    """下载单张图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            ct = resp.headers.get('Content-Type', '')
            if not ct.startswith('image/') or len(data) < 3 * 1024:
                return False
            with open(save_path, 'wb') as f:
                f.write(data)
            return True
    except Exception:
        return False


def main():
    print("=" * 60)
    print("  动物图片下载工具 (DuckDuckGo)")
    print("=" * 60)

    total_ok = 0
    total_fail = 0

    for it_name, cn_name, keyword in NEW_CLASSES:
        class_dir = os.path.join(TARGET_DIR, it_name)
        os.makedirs(class_dir, exist_ok=True)

        existing = [f for f in os.listdir(class_dir)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        need = IMAGES_PER_CLASS - len(existing)

        print(f"\n[{it_name}] {cn_name}  已有 {len(existing)} 张，还需 {need} 张")

        if need <= 0:
            print("  已足够，跳过")
            continue

        print(f"  正在搜索 '{keyword}'...")
        img_urls = search_images_ddg(keyword, need * 2)
        print(f"  找到 {len(img_urls)} 个图片链接")

        if not img_urls:
            print("  无可用链接，跳过")
            continue

        downloaded = 0
        failed = 0
        existing_set = {os.path.splitext(f)[0] for f in existing}

        for i, img_url in enumerate(img_urls):
            if downloaded >= need:
                break

            ext = '.jpg'
            if '.png' in img_url.lower():
                ext = '.png'

            filename = f"{it_name}_{len(existing) + downloaded + 1}{ext}"
            save_path = os.path.join(class_dir, filename)

            sys.stdout.write(f"\r  下载 {downloaded+1}/{need}: {filename[:25]:25s}...")
            sys.stdout.flush()

            if download_image(img_url, save_path):
                downloaded += 1
            else:
                failed += 1

            time.sleep(0.3)

        print(f"\n  [{it_name}] 完成: 成功 {downloaded} 张, 失败 {failed} 张")
        total_ok += downloaded
        total_fail += failed

    print("\n" + "=" * 60)
    print(f"  全部完成！共下载 {total_ok} 张, 失败 {total_fail} 张")
    print("=" * 60)


if __name__ == "__main__":
    main()
