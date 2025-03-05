#!/usr/bin/env python
"""
Batch crawler for multiple puzzle product pages
Usage: python batch_crawl.py products.csv [--delay 0]

The CSV file should contain product URLs in the second column.
The --delay parameter is optional and sets the delay time between crawls (seconds), default is 0.
"""

import sys
import time
import os
import argparse

# Ensure parent directory in PATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from scripts.crawler_utils import run_spider, read_urls_from_csv, logger

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Batch crawl multiple product pages')
    parser.add_argument('csv_file', help='Path to CSV file containing URLs')
    parser.add_argument('--delay', type=int, default=0, help='Delay time between crawls (seconds), default is 0')
    return parser.parse_args()

def main():
    """Main program"""
    args = parse_args()
    
    # Read URLs from CSV file
    csv_file_path = args.csv_file
    logger.info(f"Reading CSV file: {csv_file_path}...")
    urls = read_urls_from_csv(csv_file_path)
    
    if not urls:
        logger.error("No valid URLs found")
        return 1
    
    logger.info(f"Found {len(urls)} URLs, starting crawl...")
    
    # Track crawl results
    success_count = 0
    failed_urls = []
    
    # Crawl each URL
    for i, url in enumerate(urls, 1):
        logger.info(f"\n[{i}/{len(urls)}] Crawling: {url}")
        
        # Run spider (with minimal logging)
        try:
            if run_spider(url, verbose=False):
                success_count += 1
                logger.info(f"[{i}/{len(urls)}] Crawl successful: {url}")
            else:
                failed_urls.append(url)
                logger.warning(f"[{i}/{len(urls)}] Crawl failed: {url}")
        except Exception as e:
            logger.error(f"Error crawling URL: {e}")
            failed_urls.append(url)
        
        # Add delay between requests if needed
        if i < len(urls) and args.delay > 0:
            delay = args.delay
            logger.info(f"Waiting {delay} seconds before next URL...")
            time.sleep(delay)
    
    # Output statistics
    logger.info("\n======= Crawl Completed =======")
    logger.info(f"Successful: {success_count}/{len(urls)}")
    
    if failed_urls:
        logger.warning(f"Failed: {len(failed_urls)}/{len(urls)}")
        logger.warning("Failed URLs:")
        for url in failed_urls:
            logger.warning(f"  - {url}")
        
        # Save failed URLs to file
        from path_config import ROOT_DIR
        failed_file = os.path.join(ROOT_DIR, 'failed_urls.txt')
        with open(failed_file, 'w') as f:
            for url in failed_urls:
                f.write(f"{url}\n")
        logger.info(f"Failed URLs saved to {failed_file}")
    
    return 0 if success_count == len(urls) else 1

if __name__ == "__main__":
    sys.exit(main())