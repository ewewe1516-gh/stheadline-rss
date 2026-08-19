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

# 使用公用解析源或爬取頁面
gateway_url = "https://rsshub.app/stheadline/columnist/李純恩"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/plain, */*"
}

print(f"嘗試抓取標準內容...")
try:
    # 優先嘗試從高可用源獲取標準內容
    response = requests.get(gateway_url, headers=headers, timeout=25)
    if response.status_code == 200:
        os.makedirs("public", exist_ok=True)
        with open("public/feed.xml", "wb") as f:
            f.write(response.content)
        print("Successfully generated from source!")
        exit(0)
except Exception as e:
    print(f"Gateway fetch failed: {e}")

# 若 Gateway 失敗則生成提示性 RSS，確保程式能結束
print(f"解析失敗，生成空白 RSS...")
os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>\xe6\x9d\x8e\xe7\xb4\x94\xe6\x81\xa9 - \xe5\xa5\xbd\xe5\xa5\xbd\xe9\x81\x8e\xe6\x97\xa5\xe5\xad\x90 (\xe5\x85\x88\xe6\x96\x87\xe7\x89\x88)</title><link>https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9</link><description>Hub \xe7\xbd\x91\xe5\xe9\x9a\x9c\xef\xbc\x8c\xe8\xaf\xbd\xe7\xa8\x8d\xe5\x90\x8e\xe5\x86\x8d\xe8\xaf\x95\xe3\x80\x82</description><item><title>\xe6\x9c\xe6\x9d\xe8\xe5\xe5\xe8\x81\x94\xe7\xbd\xe6\x9c\xe5\xe5\xe7\xe6\xe6</item></channel></rss>')

print("Fallback generated!")
