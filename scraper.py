import os
import json
import re
import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

articles = []

try:
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 嘗試從頁面內建的 JSON-LD / __NEXT_DATA__ / 腳本區塊中提取數據
        scripts = soup.find_all("script")
        for script in scripts:
            content = script.string or ""
            if "article" in content.lower() or "columnist" in content.lower():
                # 尋找 JSON 格式的文章 ID 與標題組合
                matches = re.findall(r'"id"\s*:\s*(\d+).*?"title"\s*:\s*"([^"]+)"', content)
                for art_id, title in matches:
                    link = f"https://www.stheadline.com/columnist/article/{art_id}"
                    if not any(a["link"] == link for a in articles):
                        articles.append({"title": title, "link": link})

        # 2. 備用方案：若腳本沒擷取到，直接解析所有 HTML <a> 標籤
        if not articles:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if "/article/" in href and len(title) > 2:
                    full_link = href if href.startswith("http") else f"https://www.stheadline.com{href}"
                    if not any(item["link"] == full_link for item in articles):
                        articles.append({"title": title, "link": full_link})

        print(f"Extracted {len(articles)} articles!")
except Exception as e:
    print(f"Fetch failed: {e}")

# 寫入 RSS
for art in articles[:15]:
    feed.add_item(
        title=art["title"],
        link=art["link"],
        description=f"<p>點擊閱讀星島專欄全文：<a href='{art['link']}'>{art['title']}</a></p>"
    )

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("RSS generation process finished.")
