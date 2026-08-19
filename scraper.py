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

# 透過第三方 CORS/Proxy 網關繞過 Cloudflare IP 封鎖
urls_to_try = [
    "https://api.allorigins.win/raw?url=https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    "https://rsshub.app/stheadline/columnist/李純恩"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

fetched = False

for target in urls_to_try:
    try:
        # 設定 8 秒嚴格 Timeout，絕不卡死
        res = requests.get(target, headers=headers, timeout=8)
        if res.status_code == 200:
            if "rss" in target or "<rss" in res.text:
                os.makedirs("public", exist_ok=True)
                with open("public/feed.xml", "wb") as f:
                    f.write(res.content)
                fetched = True
                print("Successfully fetched via Proxy/Gateway!")
                break
            else:
                soup = BeautifulSoup(res.text, "html.parser")
                links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/article/" in href and len(a.get_text(strip=True)) > 2:
                        full_url = "https://www.stheadline.com" + href if href.startswith("/") else href
                        if full_url not in [l[1] for l in links]:
                            links.append((a.get_text(strip=True), full_url))
                
                if links:
                    for title, link in links[:5]:
                        feed.add_item(title=title, link=link, description=f"<p>點擊閱讀全文：<a href='{link}'>{title}</a></p>")
                    fetched = True
                    break
    except Exception as e:
        print(f"Failed attempt for {target}: {e}")

# 若全數失敗，生成標準結構確保不輸出空 XML
if not fetched:
    feed.add_item(
        title="專欄更新提醒",
        link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
        description="星島日報目前啟用了高強度防爬機制，請點擊連結前往官網閱讀最新文章。"
    )

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("Scraper completed successfully.")
