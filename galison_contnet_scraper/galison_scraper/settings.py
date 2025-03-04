BOT_NAME = "galison_scraper"

SPIDER_MODULES = ["galison_scraper.spiders"]
NEWSPIDER_MODULE = "galison_scraper.spiders"

# 遵守robots.txt規則
ROBOTSTXT_OBEY = True

# 配置user agent以避免被封
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

# 下載延遲，避免請求過於頻繁
DOWNLOAD_DELAY = 2

# 圖片存儲設置 - 使用相對路徑
# 從crawler_utils導入路徑定義，如果不可用則使用相對路徑
try:
    import os
    import sys
    # 添加scripts目錄到Python路徑
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(project_root, 'scripts')
    if scripts_dir not in sys.path:
        sys.path.append(scripts_dir)
    from scripts.crawler_utils import RELATIVE_IMAGES_PATH
    IMAGES_STORE = RELATIVE_IMAGES_PATH
except ImportError:
    IMAGES_STORE = '../galison_contnet_scraper/outputs/images'

# 啟用圖片下載管道和產品信息存儲管道
ITEM_PIPELINES = {
   "galison_scraper.pipelines.GalisonImagesPipeline": 1,
   "galison_scraper.pipelines.GalisonProductInfoPipeline": 300,
}

# 配置請求頭
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "Referer": "https://www.galison.com/",
} 