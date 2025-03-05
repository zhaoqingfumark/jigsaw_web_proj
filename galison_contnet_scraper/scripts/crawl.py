#!/usr/bin/env python
"""
Puzzle product crawler script
Usage: python crawl.py [URL]
If no URL is provided, the default URL will be used
"""

import sys
import os
import argparse

# Ensure parent directory in PATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from scripts.crawler_utils import run_spider, logger

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Crawl a single puzzle product page')
    parser.add_argument('url', nargs='?', help='URL to crawl (optional)')
    return parser.parse_args()

def main():
    """Main program"""
    args = parse_args()
    url = args.url
    
    logger.info("===== Single URL Crawler Started =====")
    success = run_spider(url)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())