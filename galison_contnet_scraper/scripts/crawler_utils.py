#!/usr/bin/env python
"""
Crawler Utility Module
Contains shared functions for URL validation, crawler execution, etc.
"""

import os
import subprocess
import logging
from urllib.parse import urlparse

# Dynamically calculate project root directory (instead of hardcoding)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define log and output directories
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs')

# Use relative path settings consistent with settings.py
# Paths relative to the Scrapy project directory
RELATIVE_IMAGES_PATH = '../galison_contnet_scraper/outputs/images'
RELATIVE_INFOS_PATH = '../galison_contnet_scraper/outputs/infos'

# Provide absolute paths for direct use in scripts
IMAGES_DIR = os.path.join(ROOT_DIR, 'outputs', 'images')
INFOS_DIR = os.path.join(ROOT_DIR, 'outputs', 'infos')

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(INFOS_DIR, exist_ok=True)

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

def read_urls(file_path):
    """Read URL list from file
    
    Args:
        file_path: Path to URL file
        
    Returns:
        list: List of URLs
    """
    urls = []
    try:
        # Handle relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(ROOT_DIR, file_path)
            
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Ignore empty lines and comments
                    urls.append(url)
        return urls
    except FileNotFoundError:
        logger.error(f"URL file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading URL file: {e}")
        return []

# Export output directory paths for other modules
def get_info_dir():
    """Get product info storage directory"""
    return INFOS_DIR

def get_images_dir():
    """Get images storage directory"""
    return IMAGES_DIR 