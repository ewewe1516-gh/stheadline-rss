import os
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from playwright.sync_api import sync_playwright

# 1. 初始化 RSS
feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

target_url = "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"

with sync_playwright() as p:
    # 啟動 Chrome 無頭瀏覽器繞過 Cloudflare 檢測
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    # 造訪李純恩專欄頁面
    page.goto(target_url, wait_until="networkidle", timeout=30000)
    soup = BeautifulSoup(page.content(), "html.parser")

    # 搜尋專欄文章連結
    articles = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.text.strip()
        if "/opinion/" in href and len(title) > 4:
            full_url = urljoin(target_url, href)
            if not any(item["link"] == full_url for item in articles):
                articles.append({"title": title, "link": full_url})

    # 逐篇進去抓取完整內文 (取最新 5 篇)
    for art in articles[:5]:
        try:
            page.goto(art["link"], wait_until="networkidle", timeout=20000)
            art_soup = BeautifulSoup(page.content(), "html.parser")

            # 抓取星島文章正文區塊
            content_div = art_soup.select_one(".article-content, .news-detail-content, .content")
            if content_div:
                # 移除不必要的廣告或推播標籤
                for s in content_div.select("script, style, .ad, .banner"):
                    s.decompose()
                full_content = str(content_div)
            else:
                full_content = "<p>內文解析失敗，請點擊連結查看原文。</p>"

            feed.add_item(
                title=f"[好好過日子] {art['title']}",
                link=art["link"],
                description=full_content # 將完整 HTML 內文放入 RSS
            )
        except Exception as e:
            print(f"抓取文章內容失敗 {art['link']}: {e}")

    browser.close()

# 匯出 XML 檔案
os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, "utf-8")

print("全文 RSS 產生完成！")
