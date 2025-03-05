"""
General Utility Module
"""
import re
import os
import hashlib

def sanitize_filename(name):
    """Clean filename by removing invalid characters"""
    # Remove punctuation and replace spaces
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    return sanitized

def generate_folder_path(product_number, title):
    """Generate product folder name (product id + product name)"""
    clean_title = sanitize_filename(title)
    return f"{product_number}_{clean_title}"

def hash_url(url):
    """Hash URL to generate unique identifier"""
    return hashlib.md5(url.encode()).hexdigest() 