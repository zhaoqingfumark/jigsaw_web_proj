#!/usr/bin/env python
"""
統一的爬蟲執行入口
用法: 
  python run.py crawl [URL]        # 執行單一爬蟲
  python run.py batch urls.txt     # 執行批量爬蟲
  python run.py batch urls.txt --delay 3  # 指定延遲時間
"""

import sys
import os
import argparse

# 將腳本目錄添加到 Python 路徑
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, script_dir)

# 導入日誌設定
from scripts.crawler_utils import logger

def main():
    """主入口函數"""
    parser = argparse.ArgumentParser(description='Galison爬蟲執行工具')
    subparsers = parser.add_subparsers(dest='command', help='要執行的命令')
    
    # 單一爬蟲命令
    crawl_parser = subparsers.add_parser('crawl', help='執行單一URL爬蟲')
    crawl_parser.add_argument('url', nargs='?', help='要爬取的URL（可選）')
    
    # 批量爬蟲命令
    batch_parser = subparsers.add_parser('batch', help='執行批量URL爬蟲')
    batch_parser.add_argument('url_file', help='包含URL的文本文件路徑')
    batch_parser.add_argument('--delay', type=int, default=5, help='爬蟲間的延遲時間（秒）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    logger.info(f"===== Galison爬蟲工具啟動 - 執行 {args.command} 命令 =====")
    
    if args.command == 'crawl':
        try:
            # 動態導入以避免循環依賴
            from scripts.crawl import main as run_single
            # 重建參數
            sys.argv = [sys.argv[0]]
            if hasattr(args, 'url') and args.url:
                sys.argv.append(args.url)
            return run_single()
        except Exception as e:
            logger.error(f"執行單一爬蟲時出錯: {str(e)}")
            return 1
            
    elif args.command == 'batch':
        try:
            # 動態導入以避免循環依賴
            from scripts.batch_crawl import main as run_batch
            # 重建參數
            sys.argv = [sys.argv[0], args.url_file]
            if hasattr(args, 'delay'):
                sys.argv.extend(['--delay', str(args.delay)])
            return run_batch()
        except Exception as e:
            logger.error(f"執行批量爬蟲時出錯: {str(e)}")
            return 1
    
    # 這裡不應該到達，但以防萬一
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main()) 