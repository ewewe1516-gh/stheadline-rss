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

# 使用 JSDelivr / CrossOrigin 代理繞過 Cloudflare 封鎖
target_api = "https://www.stheadline.com/api/getColumns?columnistId=%E6%9D%8E%E7%B4%94%E6%81%A9"
proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(target_api)}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

fetched = False

try:
    res = requests.get(proxy_url, headers=headers, timeout=15)
    if res.status_code == 200:
        data = res.json()
        contents = json.loads(data.get("contents", "{}"))
        
        # 解析文章列表
        articles = contents.get("data", []) or contents.get("items", [])
        if articles:
            for art in articles[:5]:
                title = art.get("title") or art.get("headline", "好好過日子")
                art_id = art.get("id") or art.get("article_id")
                link = f"https://www.stheadline.com/columnist/article/{art_id}" if art_id else feed.feed["link"]
                
                # 抓取摘要或內文
                summary = art.get("summary") or art.get("description") or f"<p>請前往星島頭條閱讀全文：<a href='{link}'>{title}</a></p>"
                
                feed.add_item(
                    title=title,
                    link=link,
                    description=summary
                )
            fetched = True
except Exception as e:
    print(f"Proxy fetch error: {e}")

# 若代理 API 失敗，嘗試後備 HTML 代理
if not fetched:
    try:
        html_proxy = "https://api.allorigins.win/get?url=" + requests.utils.quote("https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9")
        res = requests.get(html_proxy, headers=headers, timeout=15)
        if res.status_code == 200:
            html_text = res.json().get("contents", "")
            soup = BeautifulSoup(html_text, "html.parser")
            
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if ("/article/" in href or "/columnist/" in href) and len(title) > 2:
                    full_link = "https://www.stheadline.com" + href if href.startswith("/") else href
                    if not any(item[1] == full_link for item in links):
                        links.append((title, full_link))
            
            for title, link in links[:5]:
                feed.add_item(
                    title=f"[好好過日子] {title}",
                    link=link,
                    description=f"<p>點擊連結查看全文內容：<a href='{link}'>{title}</a></p>"
                )
            fetched = True
    except Exception as e:
        print(f"HTML Proxy error: {e}")

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("Done!")
