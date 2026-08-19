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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# 星島專欄文章列表 API / HTML 頁面
url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

# 尋找頁面內的所有文章連結
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/article/single/" in href or "/columnist/article/" in href:
        full_link = "https://www.stheadline.com" + href if href.startswith("/") else href
        if full_link not in links:
            links.append((a.get_text(strip=True), full_link))

for title, link in links[:5]:
    try:
        art_res = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_res.text, "html.parser")
        
        # 內文標籤
        content = art_soup.find("div", class_="paragraph") or art_soup.find("div", class_="article-content")
        body = str(content) if content else f"<p>全文請至：<a href='{link}'>{title}</a></p>"
        
        feed.add_item(
            title=title or "李純恩專欄文章",
            link=link,
            description=body
        )
    except Exception as e:
        print(f"Error: {e}")

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")
print("Done!")
