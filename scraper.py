import os
import json
import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.stheadline.com/"
}

# 使用備用解析網關獲取星島專欄資料
api_endpoints = [
    "https://rsshub.rss3.io/stheadline/columnist/李純恩",
    "https://rsshub.app/stheadline/columnist/李純恩"
]

success = False

for endpoint in api_endpoints:
    try:
        res = requests.get(endpoint, headers=headers, timeout=12)
        if res.status_code == 200 and len(res.content) > 200:
            os.makedirs("public", exist_ok=True)
            with open("public/feed.xml", "wb") as f:
                f.write(res.content)
            print("Successfully updated RSS from fallback gateway!")
            success = True
            break
    except Exception as e:
        print(f"Endpoint {endpoint} failed: {e}")

if not success:
    # 若被嚴格攔截，維持輸出引導連結項目
    feed.add_item(
        title="[星島專欄] 李純恩 - 好好過日子 最新文章",
        link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
        description="由於星島網頁防護機制更新，請點擊連結前往官網閱讀最新專欄文章。"
    )
    os.makedirs("public", exist_ok=True)
    with open("public/feed.xml", "w", encoding="utf-8") as f:
        feed.write(f, "utf-8")

print("Finished!")
