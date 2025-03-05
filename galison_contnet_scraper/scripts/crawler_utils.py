#!/usr/bin/env python
"""
Crawler Utility Module
Contains shared functions for URL validation, crawler execution, etc.
"""

import os
import subprocess
import logging
from urllib.parse import urlparse
import sys
import csv

# Ensure parent directory in PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import path configuration
from path_config import (
    LOGS_DIR, IMAGES_DIR, INFOS_DIR, ROOT_DIR, 
    RELATIVE_IMAGES_PATH, RELATIVE_INFOS_PATH
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "crawler.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_url(url):
    """Validate if URL is a valid Galison product page
    
    Args:
        url: URL to validate
        
    Returns:
        bool: Whether the URL is valid
    """
    if not url:
        logger.warning("URL cannot be empty")
        return False
        
    parsed = urlparse(url)
    
    if not parsed.netloc or 'galison.com' not in parsed.netloc:
        logger.warning(f"Error: URL must be a link to galison.com website - {url}")
        return False
        
    if not '/products/' in parsed.path:
        logger.warning(f"Error: URL must be a product page (containing /products/) - {url}")
        return False
    
    return True

def run_spider(url=None, verbose=True):
    """Run the spider
    
    Args:
        url: URL to crawl, if None uses the spider's default URL
        verbose: Whether to output detailed logs
        
    Returns:
        bool: Whether the spider ran successfully
    """
    if url and not validate_url(url):
        return False
    
    # Build command
    cmd = ['scrapy', 'crawl', 'puzzle']
    if url:
        cmd.extend(['-a', f'url={url}'])
    
    # Set working directory
    cwd = ROOT_DIR
    
    # Execute spider
    if verbose:
        logger.info(f"Starting crawl: {url or 'default URL'}")
    
    try:
        process = subprocess.Popen(cmd, cwd=cwd)
        process.wait()
        
        if process.returncode == 0:
            if verbose:
                logger.info("Spider completed successfully")
            return True
        else:
            logger.error(f"Spider execution failed, return code: {process.returncode}")
            return False
    except Exception as e:
        logger.error(f"Error running spider: {str(e)}")
        return False

def read_urls_from_csv(csv_file_path):
    """Read URL list from CSV file
    
    Args:
        csv_file_path: Path to CSV file containing URLs
        
    Returns:
        list: List of URLs
    """
    urls = []
    try:
        # Handle relative paths
        if not os.path.isabs(csv_file_path):
            csv_file_path = os.path.join(ROOT_DIR, csv_file_path)
            
        with open(csv_file_path, 'r') as f:
            csv_reader = csv.reader(f)
            # Skip header row
            next(csv_reader, None)
            for row in csv_reader:
                if len(row) >= 2:  # Assuming URL is in the second column (index 1)
                    url = row[1].strip()
                    if url and not url.startswith('#'):  # Ignore empty URLs and comments
                        urls.append(url)
        
        if urls:
            logger.info(f"Successfully read {len(urls)} URLs from CSV file")
        else:
            logger.warning("No valid URLs found in CSV file")
            
        return urls
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []

# Export directory path functions, maintain backward compatibility
def get_info_dir():
    """Get product info storage directory"""
    return INFOS_DIR

def get_images_dir():
    """Get images storage directory"""
    return IMAGES_DIR