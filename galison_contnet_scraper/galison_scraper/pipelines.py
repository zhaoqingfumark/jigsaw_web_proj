import json
import os
import sys
import logging
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from .utils import sanitize_filename, generate_folder_path, hash_url

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 从路径配置模块导入路径
try:
    from path_config import get_infos_dir, get_images_dir
    INFO_DIR = get_infos_dir()
    IMAGES_DIR = get_images_dir() 
    print(f"产品信息将保存到: {INFO_DIR}")
    print(f"图片将保存到: {IMAGES_DIR}")
except ImportError:
    # 回退到默认绝对路径
    INFO_DIR = os.path.join(project_root, 'outputs', 'infos')
    IMAGES_DIR = os.path.join(project_root, 'outputs', 'images')
    print(f"无法导入path_config，使用默认路径:")
    print(f"- 产品信息: {INFO_DIR}")
    print(f"- 图片: {IMAGES_DIR}")
    
# 确保目录存在
os.makedirs(INFO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# 设置日志
logger = logging.getLogger(__name__)

class GalisonImagesPipeline(ImagesPipeline):
    """Pipeline for processing image downloads"""
    
    def get_media_requests(self, item, info):
        """Generate image download requests from item"""
        if 'image_urls' not in item or not item['image_urls']:
            logger.warning(f"没有找到图片URL: {item.get('title', '未知产品')}")
            return
            
        logger.info(f"处理产品图片: {item.get('title', '未知产品')}")
        for i, image_url in enumerate(item.get('image_urls', [])):
            logger.debug(f"图片URL {i+1}: {image_url}")
            yield Request(
                url=image_url,
                meta={
                    'item': item,
                    'image_index': i
                }
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Custom image save path"""
        # 获取传递的item
        item = request.meta.get('item', {})
        image_index = request.meta.get('image_index', 0)
        
        # 获取产品信息
        product_id = item.get('product_id', 'unknown')
        product_number = item.get('product_number', product_id)
        
        # 生成清洁的文件名
        filename = f"{product_number}_{image_index+1}"
        
        # 返回图片保存路径（相对于IMAGES_STORE）
        return f'{filename}.jpg'
    
    def item_completed(self, results, item, info):
        """Called when all images in an item have been downloaded (or failed)"""
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            logger.warning(f"未能下载任何图片: {item.get('title', '未知产品')}")
        else:
            logger.info(f"成功下载 {len(image_paths)} 个图片: {item.get('title', '未知产品')}")
            
        # 添加图片路径到item
        item['images'] = image_paths
        return item


class GalisonProductInfoPipeline:
    """Pipeline for saving product information"""
    
    def process_item(self, item, spider):
        """Process item, save product info as JSON file"""
        # 获取产品信息
        product_id = item.get('product_id', 'unknown')
        product_number = item.get('product_number', product_id)
        
        # 生成文件名
        filename = f"{product_number}.json"
        
        # 保存产品信息JSON到infos目录
        file_path = os.path.join(INFO_DIR, filename)

        # 转换item为字典
        item_dict = dict(item)

        # 保存为JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item_dict, f, ensure_ascii=False, indent=4)

        logger.info(f"产品信息已保存到: {file_path}")
        return item