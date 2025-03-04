BOT_NAME = "galison_scraper"

SPIDER_MODULES = ["galison_scraper.spiders"]
NEWSPIDER_MODULE = "galison_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure user agent to avoid being banned
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

# Download delay to avoid too frequent requests
DOWNLOAD_DELAY = 2

# Image storage settings - using relative path
# Import path definitions from crawler_utils, or use relative path if unavailable
try:
    import os
    import sys
    # Add scripts directory to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(project_root, 'scripts')
    if scripts_dir not in sys.path:
        sys.path.append(scripts_dir)
    from scripts.crawler_utils import RELATIVE_IMAGES_PATH
    IMAGES_STORE = RELATIVE_IMAGES_PATH
except ImportError:
    IMAGES_STORE = '../galison_contnet_scraper/outputs/images'

# Enable image download pipeline and product info storage pipeline
ITEM_PIPELINES = {
   "galison_scraper.pipelines.GalisonImagesPipeline": 1,
   "galison_scraper.pipelines.GalisonProductInfoPipeline": 300,
}

# Configure request headers
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "Referer": "https://www.galison.com/",
} 