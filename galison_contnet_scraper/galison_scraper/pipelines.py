import json
import os
import sys
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from .utils import sanitize_filename, generate_folder_path, hash_url

# 添加scripts目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, 'scripts')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# 從crawler_utils導入目錄設置
try:
    from crawler_utils import get_info_dir, RELATIVE_INFOS_PATH
    INFO_DIR = get_info_dir()
except ImportError:
    # 如果無法導入，使用相對路徑
    INFO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'galison_contnet_scraper', 'outputs', 'infos')

# 確保信息目錄存在
os.makedirs(INFO_DIR, exist_ok=True)

class GalisonImagesPipeline(ImagesPipeline):
    """處理圖片下載的管道"""
    
    def get_media_requests(self, item, info):
        """從項目生成圖片下載請求"""
        for image_url in item.get('image_urls', []):
            yield Request(image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None, *, item=None):
        """自定義圖片保存路徑"""
        item = request.meta['item']
        # 獲取產品信息
        product_number = item.get('product_number', 'unknown')
        title = item.get('title', 'Untitled')
        
        # 生成文件夾名稱
        folder = generate_folder_path(product_number, title)
        
        # 對圖片URL進行哈希處理，生成唯一檔案名
        image_guid = hash_url(request.url)
        
        # 返回圖片保存路徑
        return f'{folder}/{image_guid}.jpg'


class GalisonProductInfoPipeline:
    """處理產品信息保存的管道"""
    
    def process_item(self, item, spider):
        """處理項目，保存產品信息為JSON文件"""
        # 獲取產品信息
        product_number = item.get('product_number', 'unknown')
        title = item.get('title', 'Untitled')
        
        # 生成文件夾名稱
        folder_name = generate_folder_path(product_number, title)
        
        # 確保目錄存在
        os.makedirs(INFO_DIR, exist_ok=True)

        # 保存產品信息JSON到infos目錄
        file_path = os.path.join(INFO_DIR, f'{folder_name}.json')

        # 將項目轉換為字典
        item_dict = {key: item.get(key, '') for key in [
            'title', 'price', 'description', 'author', 
            'product_number', 'product_details', 'image_urls'
        ]}

        # 保存為JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item_dict, f, ensure_ascii=False, indent=4)

        spider.logger.info(f"產品信息已保存至: {file_path}")
        return item 