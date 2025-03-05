#!/usr/bin/env python3
"""
从网站地图中提取包含指定关键词的URL，并保存为CSV格式
可通过修改配置变量适应不同网站
"""

import requests
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote
import csv
import os
import sys

# ===== 站点配置 - 修改这些变量以适应不同网站 =====
SITE_NAME = "galison"                   # 网站名称，用于输出文件命名
SITE_URL = "https://www.galison.com"    # 网站基础URL
MAIN_SITEMAP = f"{SITE_URL}/sitemap.xml" # 主站点地图URL
KEYWORD = "puzzle"                      # 要提取的关键词
FILTER_EXACT_WORD = True                # 是否精确匹配整词
OUTPUT_FILENAME = f"{SITE_NAME}_{KEYWORD}s" # 输出文件名基础

# 可能的其他sitemap路径模式，会自动加入到检索列表
ADDITIONAL_SITEMAP_PATTERNS = [
    "{site_url}/sitemap.xml",
    "{site_url}/sitemap_products_1.xml",
    "{site_url}/sitemap_collections_1.xml",
    "{site_url}/sitemap_pages_1.xml",
    "{site_url}/collections/{keyword}-{keyword}s/sitemap.xml",
    "{site_url}/products/sitemap.xml",
    "{site_url}/sitemap_products_2.xml",
    "{site_url}/collections/sitemap.xml",
    "{site_url}/products/{keyword}s/sitemap.xml",
    "{site_url}/collections/{keyword}s/sitemap.xml"
]

# HTTP请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# XML命名空间
XML_NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

def log(message, level="INFO"):
    """简单的日志函数"""
    print(f"[{level}] {message}")

def get_all_sitemaps(main_sitemap_url=MAIN_SITEMAP):
    """获取所有的sitemap URL"""
    try:
        log(f"获取主 sitemap: {main_sitemap_url}")
        response = requests.get(main_sitemap_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # 解析主sitemap
        root = ET.fromstring(response.content)
        sitemaps = []
        
        # 从主sitemap中提取所有子sitemap
        for sitemap in root.findall(".//sm:sitemap/sm:loc", XML_NAMESPACE):
            if sitemap.text:
                sitemaps.append(sitemap.text)
                log(f"找到 sitemap: {sitemap.text}")
        
        # 添加其他可能的sitemap
        additional_sitemaps = []
        for pattern in ADDITIONAL_SITEMAP_PATTERNS:
            sitemap_url = pattern.format(site_url=SITE_URL, keyword=KEYWORD)
            additional_sitemaps.append(sitemap_url)
        
        for sitemap in additional_sitemaps:
            if sitemap not in sitemaps:
                log(f"添加额外的 sitemap: {sitemap}")
                sitemaps.append(sitemap)
                
        return sitemaps
    except Exception as e:
        log(f"获取sitemap时出错: {e}", "ERROR")
        return []

def extract_urls_from_sitemap(sitemap_url):
    """从指定的sitemap中提取所有URL"""
    try:
        log(f"从 {sitemap_url} 提取URL")
        response = requests.get(sitemap_url, headers=HEADERS, timeout=30)
        
        # 有些sitemap可能返回错误
        if response.status_code != 200:
            log(f"从 sitemap {sitemap_url} 提取 URL 时出错: {response.status_code} {response.reason}", "WARNING")
            return []
        
        # 解析sitemap XML
        root = ET.fromstring(response.content)
        urls = []
        
        # 提取所有URL
        for url_elem in root.findall(".//sm:url/sm:loc", XML_NAMESPACE):
            if url_elem.text:
                urls.append(url_elem.text)
        
        log(f"在 {sitemap_url} 中找到 {len(urls)} 个URL")
        return urls
    except Exception as e:
        log(f"从sitemap {sitemap_url} 提取URL时出错: {e}", "WARNING")
        return []

def filter_keyword_urls(urls, keyword=KEYWORD, exact_match=FILTER_EXACT_WORD):
    """过滤出包含指定关键词的URL"""
    if exact_match:
        # 精确匹配整词
        pattern = re.compile(fr'\b{keyword}\b', re.IGNORECASE)
    else:
        # 包含关键词即可
        pattern = re.compile(keyword, re.IGNORECASE)
    
    filtered_urls = [url for url in urls if pattern.search(url)]
    
    match_type = "确切单词" if exact_match else "关键词"
    log(f"从 {len(urls)} 个URL中过滤出 {len(filtered_urls)} 个包含{match_type}'{keyword}'的URL")
    return filtered_urls

def extract_product_name_from_url(url):
    """从URL中提取产品名称"""
    try:
        # 从路径中提取最后一段作为产品名称并格式化
        path = urlparse(url).path
        product_slug = path.strip('/').split('/')[-1]
        product_name = unquote(product_slug.replace('-', ' ')).title()
        
        return product_name
    except Exception as e:
        log(f"从URL {url} 提取产品名称时出错: {e}", "ERROR")
        return url  # 如果提取失败，返回原始URL

def save_results(urls_dict, base_filename=OUTPUT_FILENAME):
    """将结果保存为CSV格式"""
    # 确保目录存在
    os.makedirs(os.path.dirname(base_filename) if os.path.dirname(base_filename) else '.', exist_ok=True)
    
    # 保存为CSV
    csv_filename = f"{base_filename}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product Name', 'URL'])  # 写入标题行
        for url, name in urls_dict.items():
            writer.writerow([name, url])
    log(f"已将 {len(urls_dict)} 个产品保存到 {csv_filename}")

def main():
    """主函数"""
    log(f"开始从 {SITE_NAME} 网站地图获取包含'{KEYWORD}'关键字的URL...")
    
    # 获取所有sitemap
    sitemaps = get_all_sitemaps()
    if not sitemaps:
        log("未能获取任何sitemap，请检查网络连接或网站结构", "ERROR")
        return
    
    # 从所有sitemap中提取URL
    all_urls = []
    for sitemap in sitemaps:
        urls = extract_urls_from_sitemap(sitemap)
        all_urls.extend(urls)
    
    log(f"总共从所有sitemap中提取了 {len(all_urls)} 个URL")
    
    # 过滤出包含关键词的URL并提取产品名称
    filtered_urls = filter_keyword_urls(all_urls)
    product_dict = {url: extract_product_name_from_url(url) for url in filtered_urls}
    
    log(f"成功提取了 {len(product_dict)} 个产品信息")
    
    # 保存结果
    save_results(product_dict)
    
    log(f"总共找到 {len(product_dict)} 个产品")
    log("完成!")

if __name__ == "__main__":
    # 允许从命令行参数覆盖配置
    if len(sys.argv) > 1:
        SITE_NAME = sys.argv[1]
    if len(sys.argv) > 2:
        SITE_URL = sys.argv[2]
    if len(sys.argv) > 3:
        KEYWORD = sys.argv[3]
        OUTPUT_FILENAME = f"{SITE_NAME}_{KEYWORD}s"
    
    main() 