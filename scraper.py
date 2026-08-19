import os
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# 抓取星島專欄 API，直接避開前端動態渲染
api_url = "https://www.stheadline.com/api/getColumns?columnistId=%E6%9D%8E%E7%B4%94%E6%81%A9"

try:
    res = requests.get(api_url, headers=headers, timeout=10)
    if res.status_code == 200 and "data" in res.json():
        articles = res.json()["data"][:5]
        for art in articles:
            title = art.get("title", "好好過日子")
            article_id = art.get("id")
            link = f"https://www.stheadline.com/columnist/article/{article_id}"
            
            # 抓取內文
            art_res = requests.get(link, headers=headers, timeout=8)
            art_soup = BeautifulSoup(art_res.text, "html.parser")
            content_div = art_soup.select_one(".paragraph, .article-content")
            
            body = str(content_div) if content_div else f"<p>請前往原文閱讀：<a href='{link}'>{title}</a></p>"
            feed.add_item(title=title, link=link, description=body)
except Exception as e:
    print(f"API Fetch Error: {e}")

# 確保輸出目錄與檔案存在
os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("Done!")
