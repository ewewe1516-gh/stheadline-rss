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

# 採用兩套不同轉譯 API 做雙保險
target_url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
proxies = [
    f"https://r.jina.ai/{target_url}",
    f"https://corsproxy.io/?{target_url}"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

articles = []

for proxy in proxies:
    try:
        res = requests.get(proxy, headers=headers, timeout=15)
        if res.status_code == 200:
            content = res.text
            # 方案 A: 透過 BeautifulSoup 提取 <a> 標籤
            soup = BeautifulSoup(content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if ("columnist/article/" in href or "/article/" in href) and len(title) > 2:
                    full_link = href if href.startswith("http") else f"https://www.stheadline.com{href}"
                    if not any(item["link"] == full_link for item in articles):
                        articles.append({"title": title, "link": full_link})
            
            # 方案 B: 若解析不到，改用純文字標記搜尋
            if not articles:
                lines = content.split("\n")
                for line in lines:
                    if "article/" in line and "http" in line:
                        # 嘗試抽取網址
                        parts = line.split("http")
                        for p in parts[1:]:
                            clean_url = "http" + p.split(" ")[0].split(")")[0].split('"')[0]
                            if "/article/" in clean_url:
                                articles.append({"title": "好好過日子 專欄文章", "link": clean_url})

            if articles:
                break
    except Exception as e:
        print(f"Proxy attempt failed: {e}")

# 寫入 RSS Item
for art in articles[:10]:
    feed.add_item(
        title=art["title"],
        link=art["link"],
        description=f"<p>點擊查看星島專欄全文：<a href='{art['link']}'>{art['title']}</a></p>"
    )

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print(f"Done! Extracted {len(articles)} articles.")
