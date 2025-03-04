"""
通用工具函數模組
"""
import re
import os
import hashlib

def sanitize_filename(name):
    """清理文件名，移除不合法字符"""
    # 移除標點符號並替換空格
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    return sanitized

def generate_folder_path(product_number, title):
    """生成產品文件夾名稱 (產品id+產品名)"""
    clean_title = sanitize_filename(title)
    return f"{product_number}_{clean_title}"

def hash_url(url):
    """對URL進行哈希處理，生成唯一標識"""
    return hashlib.md5(url.encode()).hexdigest() 