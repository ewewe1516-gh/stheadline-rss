import os
import json
import re
from playwright.sync_api import sync_playwright
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

target_url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
articles = []

with sync_playwright() as p:
    # 啟動 Chromium 無頭瀏覽器
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    try:
        # 載入頁面並等待 JS 渲染
        page.goto(target_url, wait_until="networkidle", timeout=30000)
        html_content = page.content()

        # 優先從渲染後的 DOM 提取 HTML <a> 標籤
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True)
            if "/columnist/article/" in href and len(title) > 2:
                full_link = href if href.startswith("http") else f"https://www.stheadline.com{href}"
                if not any(item["link"] == full_link for item in articles):
                    articles.append({"title": title, "link": full_link})

        print(f"Playwright successfully extracted {len(articles)} articles!")

    except Exception as e:
        print(f"Playwright execution error: {e}")
    finally:
        browser.close()

# 寫入 RSS Item
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
