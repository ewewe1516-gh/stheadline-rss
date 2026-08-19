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

# 使用 Jina AI Reader 繞過 Cloudflare 防火牆提取網頁文字內容
jina_url = "https://r.jina.ai/https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    res = requests.get(jina_url, headers=headers, timeout=25)
    if res.status_code == 200:
        text = res.text
        lines = text.split("\n")
        
        # 解析 Jina 轉譯出的 Markdown 連結與標題
        items = []
        for line in lines:
            if "](" in line and "/article/" in line:
                # 提取 Markdown 格式的 [標題](URL)
                try:
                    title = line.split("](")[0].replace("[", "").strip()
                    url = line.split("](")[1].split(")")[0].strip()
                    if title and url and len(title) > 2:
                        if not any(i['url'] == url for i in items):
                            items.append({"title": title, "url": url})
                except Exception:
                    continue

        # 寫入 RSS Item
        for item in items[:8]:
            feed.add_item(
                title=item["title"],
                link=item["url"],
                description=f"<p>點擊閱讀星島專欄全文：<a href='{item['url']}'>{item['title']}</a></p>"
            )
except Exception as e:
    print(f"Fetch error: {e}")

# 確保目錄存在並輸出 xml
os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("RSS build completed successfully!")
