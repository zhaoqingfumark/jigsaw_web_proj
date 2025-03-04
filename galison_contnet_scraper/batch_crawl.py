#!/usr/bin/env python
"""
批量爬取多個拼圖產品頁面
用法: python batch_crawl.py urls.txt
其中urls.txt是包含多個URL的文本文件，每行一個URL
"""

import sys
import time
from crawl import run_spider, validate_url

def read_urls(file_path):
    """從文件中讀取URL列表"""
    urls = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # 忽略空行和註釋
                    urls.append(url)
        return urls
    except Exception as e:
        print(f"讀取URL文件出錯: {e}")
        return []

def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("用法: python batch_crawl.py urls.txt")
        return False
    
    # 讀取URL文件
    url_file = sys.argv[1]
    urls = read_urls(url_file)
    
    if not urls:
        print("未找到有效URL")
        return False
    
    print(f"找到 {len(urls)} 個URL，開始爬取...")
    
    # 統計爬取結果
    success_count = 0
    failed_urls = []
    
    # 逐個爬取URL
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 正在爬取: {url}")
        
        # 驗證URL
        if not validate_url(url):
            print(f"無效URL，跳過: {url}")
            failed_urls.append(url)
            continue
        
        # 運行爬蟲
        if run_spider(url):
            success_count += 1
        else:
            failed_urls.append(url)
        
        # 延遲一段時間，避免頻繁請求
        if i < len(urls):
            print("等待5秒後繼續爬取下一個URL...")
            time.sleep(5)
    
    # 輸出統計信息
    print("\n======= 爬取完成 =======")
    print(f"成功: {success_count}/{len(urls)}")
    
    if failed_urls:
        print(f"失敗: {len(failed_urls)}/{len(urls)}")
        print("失敗的URL:")
        for url in failed_urls:
            print(f"  - {url}")
    
    return success_count == len(urls)

if __name__ == "__main__":
    main() 