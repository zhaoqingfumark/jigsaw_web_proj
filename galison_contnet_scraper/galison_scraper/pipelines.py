import json
import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import hashlib
import re

class GalisonImagesPipeline(ImagesPipeline):
    """處理圖片下載的管道"""
    
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url, meta={'item': item})

    def folder_path(self, item):
        """生成產品文件夾名稱 (產品id+產品名)"""
        product_number = item.get('product_number', 'unknown')
        title = self.sanitize_filename(item['title'])
        return f"{product_number}_{title}"
    
    def sanitize_filename(self, name):
        """清理文件名，移除不合法字符"""
        # 移除標點符號並替換空格
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        return sanitized

    def file_path(self, request, response=None, info=None, *, item=None):
        """自定義圖片保存路徑"""
        item = request.meta['item']
        # 使用產品id+產品名稱作為文件夾名稱
        folder = self.folder_path(item)
        # 使用圖片URL的哈希值作為檔案名
        image_guid = hashlib.md5(request.url.encode()).hexdigest()
        # 返回圖片保存路徑
        return f'{folder}/{image_guid}.jpg'

class GalisonProductInfoPipeline:
    """處理產品信息保存的管道"""
    
    def sanitize_filename(self, name):
        """清理文件名，移除不合法字符"""
        # 移除標點符號並替換空格
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        return sanitized

    def folder_path(self, item):
        """生成產品文件夾名稱 (產品id+產品名)"""
        product_number = item.get('product_number', 'unknown')
        title = self.sanitize_filename(item['title'])
        return f"{product_number}_{title}"
    
    def process_item(self, item, spider):
        # 獲取產品文件夾名稱
        folder_name = self.folder_path(item)
        
        # 創建產品信息目錄
        info_dir = '/Users/markus/jigsaw-proj/demo123/galison_scraper/infos'
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)

        # 保存產品信息JSON到infos目錄
        file_path = os.path.join(info_dir, f'{folder_name}.json')

        # 轉換為字典並儲存為JSON
        item_dict = {
            'title': item.get('title', ''),
            'price': item.get('price', ''),
            'description': item.get('description', ''),
            'author': item.get('author', ''),
            'product_number': item.get('product_number', ''),
            'product_details': item.get('product_details', []),
            'image_urls': item.get('image_urls', [])
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item_dict, f, ensure_ascii=False, indent=4)

        return item 