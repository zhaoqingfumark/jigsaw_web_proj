# Scrapy settings for galison_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 修改：使用绝对路径从path_config导入图片存储路径
try:
    from path_config import get_images_dir
    IMAGES_STORE = get_images_dir()
    print(f"图片将存储在: {IMAGES_STORE}")
except ImportError:
    # 回退到默认绝对路径
    IMAGES_STORE = os.path.join(project_root, 'outputs', 'images')
    print(f"无法导入path_config，图片将存储在: {IMAGES_STORE}")
    # 确保目录存在
    os.makedirs(IMAGES_STORE, exist_ok=True)

BOT_NAME = 'galison_scraper'

SPIDER_MODULES = ['galison_scraper.spiders']
NEWSPIDER_MODULE = 'galison_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure user agent to avoid being banned
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'

# Download delay to avoid too frequent requests
DOWNLOAD_DELAY = 0

# Configure request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'Referer': 'https://www.galison.com/',
}

# Enable image download pipeline and product info storage pipeline
ITEM_PIPELINES = {
    'galison_scraper.pipelines.GalisonImagesPipeline': 1,
    'galison_scraper.pipelines.GalisonProductInfoPipeline': 300,
}