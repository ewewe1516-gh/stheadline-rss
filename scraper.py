import os
import re
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from playwright.sync_api import sync_playwright

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

articles = []

def run_browser():
    global articles
    with sync_playwright() as p:
        # 啟動無頭 Chromium 瀏覽器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        target_url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
        print(f"Navigating to {target_url}...")
        
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)  # 等待 5 秒讓 JavaScript 渲染列表
            
            # 獲取完整渲染後的 HTML
            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 解析專欄文章連結
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if "/article/" in href and len(title) > 2:
                    full_link = href if href.startswith("http") else f"https://www.stheadline.com{href}"
                    if not any(item["link"] == full_link for item in articles):
                        articles.append({"title": title, "link": full_link})
        except Exception as e:
            print(f"Playwright error: {e}")
        finally:
            browser.close()

run_browser()

# 將抓取到的文章寫入 RSS
for art in articles[:10]:
    feed.add_item(
        title=art["title"],
        link=art["link"],
        description=f"<p>點擊查看星島專欄全文：<a href='{art['link']}'>{art['title']}</a></p>"
    )

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print(f"Done! Successfully generated RSS with {len(articles)} articles.")
