"""
从百度图片下载动物图片（requests 版）
用法: python baidu_download.py
"""

import os
import re
import json
import time
import sys
import requests
import urllib.parse
import urllib3
urllib3.disable_warnings()

# ── 要下载的动物（补充现有数据集中的类到100张） ──
EXISTING_CLASSES = {
    "cane": "狗", "gatto": "猫", "cavallo": "马", "mucca": "牛",
    "pecora": "羊", "gallina": "鸡", "farfalla": "蝴蝶",
    "ragno": "蜘蛛", "elefante": "大象", "scoiattolo": "松鼠",
}

# 新增的动物
NEW_CLASSES = {
    "uccello": "鸟", "anatra": "鸭子", "coniglio": "兔子",
    "tigre": "老虎", "leone": "狮子", "scimmia": "猴子",
}

TARGET_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-img")
IMAGES_PER_CLASS = 100

session = requests.Session()
session.proxies = {'http': '', 'https': ''}
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# 初始化会话
session.get('https://image.baidu.com/', timeout=10)


def search_baidu(keyword, max_num=120):
    """百度图片搜索"""
    all_urls = []
    pn = 0
    while len(all_urls) < max_num and pn < 300:
        params = {
            'tn': 'resultjson_com', 'word': keyword,
            'pn': pn, 'rn': 60,
        }
        try:
            r = session.get('https://image.baidu.com/search/acjson',
                           params=params,
                           headers={'Referer': 'https://image.baidu.com/'},
                           timeout=15)
            raw = r.text
            raw = re.sub(r',\s*}', '}', raw)
            raw = re.sub(r',\s*]', ']', raw)
            data = json.loads(raw)

            found = 0
            for item in data.get('data', []):
                if not isinstance(item, dict):
                    continue
                u = (item.get('middleURL') or item.get('thumbURL') or '')
                if u and u.startswith('http') and u not in all_urls:
                    all_urls.append(u)
                    found += 1

            if found == 0:
                break
            pn += 60
            time.sleep(0.3)
        except Exception as e:
            print(f"    搜索出错: {type(e).__name__}")
            break

    return all_urls[:max_num]


def download_image(url, save_path):
    """下载图片"""
    for attempt in range(3):
        try:
            r = session.get(url,
                           headers={'Referer': 'https://image.baidu.com/'},
                           timeout=15)
            if r.status_code != 200:
                time.sleep(0.5)
                continue
            ct = r.headers.get('Content-Type', '')
            if not ct.startswith('image/') or len(r.content) < 3 * 1024:
                return False
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def download_class(dir_name, cn_name, search_word=None):
    """下载一个类别"""
    if search_word is None:
        search_word = cn_name

    class_dir = os.path.join(TARGET_DIR, dir_name)
    os.makedirs(class_dir, exist_ok=True)

    existing = [f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    need = IMAGES_PER_CLASS - len(existing)

    print(f"\n{'='*50}")
    print(f"[{dir_name}] {cn_name}  已有 {len(existing)} 张，还需 {need} 张")

    if need <= 0:
        print("  已足够，跳过")
        return 0, 0

    print(f"  搜索 '{search_word}'...")
    img_urls = search_baidu(search_word, need * 2)
    print(f"  找到 {len(img_urls)} 个图片链接")

    if not img_urls:
        print("  无可用链接")
        return 0, 0

    ok = 0
    fail = 0
    for i, img_url in enumerate(img_urls):
        if ok >= need:
            break

        ext = '.jpg'
        if '.png' in img_url.lower():
            ext = '.png'

        filename = f"{dir_name}_{len(existing) + ok + 1}{ext}"
        save_path = os.path.join(class_dir, filename)

        sys.stdout.write(f"\r  下载 {ok+1}/{need}...")
        sys.stdout.flush()

        if download_image(img_url, save_path):
            ok += 1
        else:
            fail += 1

        time.sleep(0.2)

    print(f"\n  [{dir_name}] 完成: 成功 {ok} 张, 失败 {fail} 张")
    return ok, fail


def main():
    print("=" * 60)
    print("  百度图片批量下载 - 动物图片")
    print("=" * 60)

    total_ok = 0
    total_fail = 0

    # 1. 已有的10类（补充到100张）
    print("\n>>> 补充已有类别 <<<")
    for dir_name, cn_name in EXISTING_CLASSES.items():
        ok, fail = download_class(dir_name, cn_name, cn_name)
        total_ok += ok
        total_fail += fail

    # 2. 新增6类
    print("\n>>> 新增类别 <<<")
    for dir_name, cn_name in NEW_CLASSES.items():
        ok, fail = download_class(dir_name, cn_name, cn_name)
        total_ok += ok
        total_fail += fail

    print("\n" + "=" * 60)
    print(f"  全部完成！成功 {total_ok} 张, 失败 {total_fail} 张")
    print("=" * 60)


if __name__ == "__main__":
    main()
