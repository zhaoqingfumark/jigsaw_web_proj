#!/usr/bin/env python
"""
Unified crawler execution entry point
Usage: 
  python run.py crawl [URL]        # Execute single crawler
  python run.py batch urls.txt     # Execute batch crawler with txt file
  python run.py batch galison_puzzles.csv  # Execute batch crawler with CSV file
  python run.py batch urls.txt --delay 3  # Specify delay time
"""

import sys
import os
import argparse

# 确保脚本目录在Python路径中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入路径配置和日志配置
from path_config import ensure_dirs_exist
from scripts.crawler_utils import logger

# 确保所有必要目录存在
ensure_dirs_exist()

def main():
    """Main entry function"""
    parser = argparse.ArgumentParser(description='Galison Crawler Execution Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Single crawler command
    crawl_parser = subparsers.add_parser('crawl', help='Execute single URL crawler')
    crawl_parser.add_argument('url', nargs='?', help='URL to crawl (optional)')
    
    # Batch crawler command
    batch_parser = subparsers.add_parser('batch', help='Execute batch URL crawler')
    batch_parser.add_argument('url_file', help='Path to file containing URLs (supports .txt or .csv format)')
    batch_parser.add_argument('--delay', type=int, default=0, help='Delay time between crawls (seconds)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    logger.info(f"===== Galison Crawler Tool Started - Executing {args.command} command =====")
    
    if args.command == 'crawl':
        try:
            # Dynamic import to avoid circular dependencies
            from scripts.crawl import main as run_single
            # Rebuild arguments
            sys.argv = [sys.argv[0]]
            if hasattr(args, 'url') and args.url:
                sys.argv.append(args.url)
            return run_single()
        except Exception as e:
            logger.error(f"Error executing single crawler: {str(e)}")
            return 1
            
    elif args.command == 'batch':
        try:
            # Dynamic import to avoid circular dependencies
            from scripts.batch_crawl import main as run_batch
            # Rebuild arguments
            sys.argv = [sys.argv[0], args.url_file]
            if hasattr(args, 'delay'):
                sys.argv.extend(['--delay', str(args.delay)])
            return run_batch()
        except Exception as e:
            logger.error(f"Error executing batch crawler: {str(e)}")
            return 1
    
    # This should not be reached, but just in case
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())