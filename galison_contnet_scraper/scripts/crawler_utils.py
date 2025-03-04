#!/usr/bin/env python
"""
爬蟲通用工具模塊
包含URL驗證、爬蟲運行等共用功能
"""

import os
import subprocess
import logging
from urllib.parse import urlparse

# 動態計算項目根目錄（而不是硬編碼）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定義日誌和輸出目錄
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs')

# 使用與settings.py一致的相對路徑設置
# 相對於Scrapy項目目錄的路徑
RELATIVE_IMAGES_PATH = '../galison_contnet_scraper/outputs/images'
RELATIVE_INFOS_PATH = '../galison_contnet_scraper/outputs/infos'

# 為腳本中直接使用提供絕對路徑
IMAGES_DIR = os.path.join(ROOT_DIR, 'outputs', 'images')
INFOS_DIR = os.path.join(ROOT_DIR, 'outputs', 'infos')

# 確保目錄存在
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(INFOS_DIR, exist_ok=True)

# 配置日誌
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
    """驗證URL是否為有效的Galison產品頁面
    
    Args:
        url: 要驗證的URL
        
    Returns:
        bool: URL是否有效
    """
    if not url:
        logger.warning("URL不能為空")
        return False
        
    parsed = urlparse(url)
    
    if not parsed.netloc or 'galison.com' not in parsed.netloc:
        logger.warning(f"錯誤: URL必須是galison.com網站的鏈接 - {url}")
        return False
        
    if not '/products/' in parsed.path:
        logger.warning(f"錯誤: URL必須是產品頁面 (包含/products/) - {url}")
        return False
    
    return True

def run_spider(url=None, verbose=True):
    """運行爬蟲
    
    Args:
        url: 要爬取的URL，如果為None則使用爬蟲默認URL
        verbose: 是否輸出詳細日誌
        
    Returns:
        bool: 爬蟲是否成功運行
    """
    if url and not validate_url(url):
        return False
    
    # 構建命令
    cmd = ['scrapy', 'crawl', 'puzzle']
    if url:
        cmd.extend(['-a', f'url={url}'])
    
    # 設置工作目錄
    cwd = ROOT_DIR
    
    # 執行爬蟲
    if verbose:
        logger.info(f"開始爬取: {url or '默認URL'}")
    
    try:
        process = subprocess.Popen(cmd, cwd=cwd)
        process.wait()
        
        if process.returncode == 0:
            if verbose:
                logger.info("爬蟲已成功完成")
            return True
        else:
            logger.error(f"爬蟲運行失敗，返回碼: {process.returncode}")
            return False
    except Exception as e:
        logger.error(f"運行爬蟲時發生錯誤: {str(e)}")
        return False

def read_urls(file_path):
    """從文件中讀取URL列表
    
    Args:
        file_path: URL文件路徑
        
    Returns:
        list: URL列表
    """
    urls = []
    try:
        # 處理相對路徑
        if not os.path.isabs(file_path):
            file_path = os.path.join(ROOT_DIR, file_path)
            
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # 忽略空行和註釋
                    urls.append(url)
        return urls
    except FileNotFoundError:
        logger.error(f"找不到URL文件: {file_path}")
        return []
    except Exception as e:
        logger.error(f"讀取URL文件出錯: {e}")
        return []

# 導出輸出目錄路徑給其他模塊使用
def get_info_dir():
    """獲取信息存儲目錄"""
    return INFOS_DIR

def get_images_dir():
    """獲取圖片存儲目錄"""
    return IMAGES_DIR 