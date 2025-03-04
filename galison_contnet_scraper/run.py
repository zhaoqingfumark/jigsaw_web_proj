#!/usr/bin/env python
"""
Unified crawler execution entry point
Usage: 
  python run.py crawl [URL]        # Execute single crawler
  python run.py batch urls.txt     # Execute batch crawler
  python run.py batch urls.txt --delay 3  # Specify delay time
"""

import sys
import os
import argparse

# Add script directory to Python path
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, script_dir)

# Import logging configuration
from scripts.crawler_utils import logger

def main():
    """Main entry function"""
    parser = argparse.ArgumentParser(description='Galison Crawler Execution Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Single crawler command
    crawl_parser = subparsers.add_parser('crawl', help='Execute single URL crawler')
    crawl_parser.add_argument('url', nargs='?', help='URL to crawl (optional)')
    
    # Batch crawler command
    batch_parser = subparsers.add_parser('batch', help='Execute batch URL crawler')
    batch_parser.add_argument('url_file', help='Path to text file containing URLs')
    batch_parser.add_argument('--delay', type=int, default=5, help='Delay time between crawls (seconds)')
    
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