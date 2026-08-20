import os
import json
import subprocess
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

# 使用 curl 繞過基本的 Python requests 封鎖
curl_cmd = [
    "curl", "-s", "-L",
    "https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "-H", "Accept-Language: zh-TW,zh;q=0.9,en;q=0.8"
]

articles = []

try:
    html_content = subprocess.check_output(curl_cmd, text=True, timeout=20)
    
    # 嘗試從 NEXT_DATA JSON 提取文章清單
    if "__NEXT_DATA__" in html_content:
        json_str = html_content.split('<script id="__NEXT_DATA__" type="application/json">')[1].split('</script>')[0]
        data = json.loads(json_str)
        
        # 遞迴尋找含有 articleId 或 id 與 title 的數據結構
        page_props = data.get("props", {}).get("pageProps", {})
        
        # 尋找頁面中的專欄文章清單
        items = page_props.get("initialData", {}).get("data", []) or page_props.get("articles", [])
        
        for item in items:
            art_id = item.get("id") or item.get("articleId")
            title = item.get("title")
            if art_id and title:
                articles.append({
                    "title": title,
                    "link": f"https://www.stheadline.com/columnist/article/{art_id}"
                })

    # 若 JSON 未能提取，使用正規表示式直接掃描文章連結結構
    if not articles:
        import re
        matches = re.findall(r'href=["\'](/columnist/article/(\d+))["\'][^>]*>(.*?)</a>', html_content)
        for path, art_id, raw_title in matches:
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            link = f"https://www.stheadline.com{path}"
            if title and not any(a["link"] == link for a in articles):
                articles.append({"title": title, "link": link})

    print(f"Successfully extracted {len(articles)} articles!")

except Exception as e:
    print(f"Fetch failed: {e}")

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

print("Finished generating public/feed.xml")
