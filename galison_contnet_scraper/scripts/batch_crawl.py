#!/usr/bin/env python
"""
批量爬取多個拼圖產品頁面
用法: python batch_crawl.py urls.txt [--delay 5]
其中urls.txt是包含多個URL的文本文件，每行一個URL
--delay參數可選，用於設置爬蟲間的延遲時間（秒）
"""

import sys
import time
import argparse
from crawler_utils import run_spider, read_urls, logger

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='批量爬取多個產品頁面')
    parser.add_argument('url_file', help='包含URL的文本文件路徑')
    parser.add_argument('--delay', type=int, default=5, help='爬蟲間的延遲時間（秒）')
    return parser.parse_args()

def main():
    """主程序"""
    args = parse_args()
    
    # 讀取URL文件
    urls = read_urls(args.url_file)
    
    if not urls:
        logger.error("未找到有效URL")
        return 1
    
    logger.info(f"找到 {len(urls)} 個URL，開始爬取...")
    
    # 統計爬取結果
    success_count = 0
    failed_urls = []
    
    # 逐個爬取URL
    for i, url in enumerate(urls, 1):
        logger.info(f"\n[{i}/{len(urls)}] 正在爬取: {url}")
        
        # 運行爬蟲 (使用簡短日誌模式)
        try:
            if run_spider(url, verbose=False):
                success_count += 1
                logger.info(f"[{i}/{len(urls)}] 爬取成功: {url}")
            else:
                failed_urls.append(url)
                logger.warning(f"[{i}/{len(urls)}] 爬取失敗: {url}")
        except Exception as e:
            logger.error(f"爬取URL時發生錯誤: {e}")
            failed_urls.append(url)
        
        # 延遲一段時間，避免頻繁請求
        if i < len(urls):
            delay = args.delay
            logger.info(f"等待{delay}秒後繼續爬取下一個URL...")
            time.sleep(delay)
    
    # 輸出統計信息
    logger.info("\n======= 爬取完成 =======")
    logger.info(f"成功: {success_count}/{len(urls)}")
    
    if failed_urls:
        logger.warning(f"失敗: {len(failed_urls)}/{len(urls)}")
        logger.warning("失敗的URL:")
        for url in failed_urls:
            logger.warning(f"  - {url}")
        
        # 保存失敗的URL到文件
        with open('failed_urls.txt', 'w') as f:
            for url in failed_urls:
                f.write(f"{url}\n")
        logger.info("已將失敗的URL保存到 failed_urls.txt")
    
    return 0 if success_count == len(urls) else 1

if __name__ == "__main__":
    sys.exit(main()) 