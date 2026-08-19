import os
import requests
from feedgenerator import Rss201rev2Feed

feed = Rss201rev2Feed(
    title="李純恩 - 好好過日子 (全文版)",
    link="https://www.stheadline.com/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9",
    description="星島日報 李純恩「好好過日子」專欄全文 RSS",
    language="zh-Hant"
)

# 使用公用高可用源或直連 API
primary_api_url = "https://rsshub.app/stheadline/columnist/%E6%9D%8E%E7%B4%94%E6%81%A9"
backup_api_url = "https://www.stheadline.com/api/getColumns?columnistId=李純恩" # 備用

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/xml, application/json; q=0.9, */*; q=0.8",
}

def fetch_rss():
    print(f"嘗試抓取 API 源...")
    try:
        # 先嘗試公用高可用解析源
        response = requests.get(primary_api_url, headers=headers, timeout=25)
        if response.status_code == 200:
            print("公用源抓取成功！")
            return response.content
    except Exception as e:
        print(f"公用源抓取失敗: {e}")

    # 若公用源失敗，嘗試寫入一個基本的 XML 結構（或你原本邏輯的简化版）
    print(f"抓取失敗，生成空白 RSS...")
    # 這裡可以選擇回傳空白、舊內容或使用 backup_api_url (邏輯較複雜，此處簡化)
    return b'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>\xe6\x9d\x8e\xe7\xb4\x94\xe6\x81\xa9 - \xe5\xa5
