#!/usr/bin/env python
"""
拼圖產品爬蟲啟動腳本
用法: python crawl.py [URL]
如果未提供URL，將使用默認URL
"""

import sys
import argparse
from crawler_utils import run_spider, logger

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='爬取單個拼圖產品頁面')
    parser.add_argument('url', nargs='?', help='要爬取的URL（可選）')
    return parser.parse_args()

def main():
    """主程序"""
    args = parse_args()
    url = args.url
    
    logger.info("===== 單一URL爬蟲啟動 =====")
    success = run_spider(url)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 