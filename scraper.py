import os
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from playwright.sync_api import sync_playwright

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

target_url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    # 開啟專欄頁面並等待加載
    page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(4000)
    
    soup = BeautifulSoup(page.content(), "html.parser")

    # 寬鬆匹配所有包含文章連結的 a 標籤
    articles = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        # 匹配星島文章 URL 特徵 (/columnist/article/ 或 /article/)
        if re.search(r'/(article|columnist|opinion)/', href) and len(title) > 2:
            full_url = urljoin("https://www.stheadline.com", href)
            if not any(item["link"] == full_url for item in articles):
                articles.append({"title": title, "link": full_url})

    # 抓取最新 5 篇內文
    for art in articles[:5]:
        try:
            page.goto(art["link"], wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            art_soup = BeautifulSoup(page.content(), "html.parser")

            # 擴充內文容器選擇器
            content_div = art_soup.select_one(".article-content, .news-detail-content, .content, .paragraph, #article-content")
            if content_div:
                for s in content_div.select("script, style, .ad, .banner, .share-btn"):
                    s.decompose()
                full_content = str(content_div)
            else:
                full_content = f"<p>請點擊連結查看全文：<a href='{art['link']}'>{art['title']}</a></p>"

            feed.add_item(
                title=f"[好好過日子] {art['title']}",
                link=art["link"],
                description=full_content
            )
        except Exception as e:
            print(f"Failed to fetch {art['link']}: {e}")

    browser.close()

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("Done!")
