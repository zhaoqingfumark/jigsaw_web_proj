import json
import os
import sys
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from .utils import sanitize_filename, generate_folder_path, hash_url

# Add scripts directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, 'scripts')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

# Import directory settings from crawler_utils
try:
    from crawler_utils import get_info_dir, RELATIVE_INFOS_PATH
    INFO_DIR = get_info_dir()
except ImportError:
    # If import fails, use relative path
    INFO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'galison_contnet_scraper', 'outputs', 'infos')

# Ensure info directory exists
os.makedirs(INFO_DIR, exist_ok=True)

class GalisonImagesPipeline(ImagesPipeline):
    """Pipeline for processing image downloads"""
    
    def get_media_requests(self, item, info):
        """Generate image download requests from item"""
        for image_url in item.get('image_urls', []):
            yield Request(image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None, *, item=None):
        """Custom image save path"""
        item = request.meta['item']
        # Get product information
        product_number = item.get('product_number', 'unknown')
        title = item.get('title', 'Untitled')
        
        # Generate folder name
        folder = generate_folder_path(product_number, title)
        
        # Hash the image URL to generate unique filename
        image_guid = hash_url(request.url)
        
        # Return image save path
        return f'{folder}/{image_guid}.jpg'


class GalisonProductInfoPipeline:
    """Pipeline for saving product information"""
    
    def process_item(self, item, spider):
        """Process item, save product info as JSON file"""
        # Get product information
        product_number = item.get('product_number', 'unknown')
        title = item.get('title', 'Untitled')
        
        # Generate folder name
        folder_name = generate_folder_path(product_number, title)
        
        # Ensure directory exists
        os.makedirs(INFO_DIR, exist_ok=True)

        # Save product info JSON to infos directory
        file_path = os.path.join(INFO_DIR, f'{folder_name}.json')

        # Convert item to dictionary
        item_dict = {key: item.get(key, '') for key in [
            'title', 'price', 'description', 'author', 
            'product_number', 'product_details', 'image_urls'
        ]}

        # Save as JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item_dict, f, ensure_ascii=False, indent=4)

        spider.logger.info(f"Product information saved to: {file_path}")
        return item 