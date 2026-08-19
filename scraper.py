import os
import requests
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

# 直接請求星島頭條專欄文章 API
api_url = "https://www.stheadline.com/api/getColumns"
params = {
    "columnistId": "李純恩",
    "page": 1,
    "limit": 10
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    "Accept": "application/json, text/plain, */*"
}

try:
    res = requests.get(api_url, params=params, headers=headers, timeout=15)
    if res.status_code == 200:
        data = res.json()
        # 兼容 API 的多種資料層級結構
        articles = data.get("data", []) if isinstance(data.get("data"), list) else data.get("data", {}).get("list", [])
        
        for art in articles:
            title = art.get("title") or art.get("headline") or "好好過日子"
            art_id = art.get("id") or art.get("article_id")
            
            if art_id:
                link = f"https://www.stheadline.com/columnist/article/{art_id}"
            else:
                link = feed.feed["link"]
                
            summary = art.get("summary") or art.get("description") or art.get("content") or f"<p>點擊查看全文：<a href='{link}'>{title}</a></p>"
            
            feed.add_item(
                title=title,
                link=link,
                description=summary
            )
            
        print(f"Successfully added {len(articles)} articles!")
    else:
        print(f"API Error: {res.status_code}")
except Exception as e:
    print(f"Fetch failed: {e}")

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")
