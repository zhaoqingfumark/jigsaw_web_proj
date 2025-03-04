#!/usr/bin/env python
"""
拼圖產品爬蟲啟動腳本
用法: python crawl.py [URL]
如果未提供URL，將使用默認URL
"""

import sys
import os
import subprocess
from urllib.parse import urlparse

def validate_url(url):
    """驗證URL是否為有效的Galison產品頁面"""
    parsed = urlparse(url)
    
    if not parsed.netloc or 'galison.com' not in parsed.netloc:
        print(f"錯誤: URL必須是galison.com網站的鏈接")
        return False
        
    if not '/products/' in parsed.path:
        print(f"錯誤: URL必須是產品頁面 (包含/products/)")
        return False
    
    return True

def run_spider(url=None):
    """運行爬蟲"""
    if url and not validate_url(url):
        return False
    
    # 構建命令
    cmd = ['scrapy', 'crawl', 'puzzle']
    if url:
        cmd.extend(['-a', f'url={url}'])
    
    # 執行爬蟲
    print(f"開始爬取: {url or '默認URL'}")
    process = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    process.wait()
    
    if process.returncode == 0:
        print("爬蟲已成功完成")
        return True
    else:
        print(f"爬蟲運行失敗，返回碼: {process.returncode}")
        return False

if __name__ == "__main__":
    # 從命令行參數獲取URL
    url = None
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    # 運行爬蟲
    run_spider(url) 