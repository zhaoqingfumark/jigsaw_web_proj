import scrapy
import re
import json
import os
import time

class UrlCollectorSpider(scrapy.Spider):
    """從Galison網站收集所有產品URL的爬蟲"""
    name = "url_collector"
    allowed_domains = ["galison.com"]
    
    # 指定初始類別頁面
    start_urls = [
        # 針對不同片數的拼圖
        "https://www.galison.com/collections/100-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/300-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/500-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/750-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/1000-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/1500-piece-jigsaw-puzzles",
        "https://www.galison.com/collections/2000-piece-jigsaw-puzzles",
        
        # 主要拼圖類別
        "https://www.galison.com/collections/jigsaw-puzzles",
        "https://www.galison.com/collections/wooden-puzzles",
        "https://www.galison.com/collections/shaped-jigsaw-puzzles",
        "https://www.galison.com/collections/mini-jigsaw-puzzles",
        "https://www.galison.com/collections/foil-jigsaw-puzzles",
        "https://www.galison.com/collections/double-sided-jigsaw-puzzles",
        "https://www.galison.com/collections/panoramic-puzzles"
    ]
    
    # 用於存儲已收集的URL，避免重複
    collected_urls = set()
    
    # 保存結果的文件路徑
    output_file = "all_product_urls.txt"
    
    # 分類黑名單，可以跳過一些不想爬取的分類
    category_blacklist = ['/collections/gifts-accessories', '/collections/sale']
    
    def __init__(self, *args, **kwargs):
        super(UrlCollectorSpider, self).__init__(*args, **kwargs)
        # 支持通過命令行參數設置輸出文件
        if 'output' in kwargs:
            self.output_file = kwargs.get('output')
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(self.output_file) if os.path.dirname(self.output_file) else '.', exist_ok=True)
        
        # 清空或創建輸出文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("# Galison產品URL列表 - 自動生成\n# 格式：URL [產品名稱]\n\n")
    
    def start_requests(self):
        """開始請求，為每個請求添加特殊的User-Agent和Cookie"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                callback=self.parse_category,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.galison.com/'
                },
                meta={'category_url': url, 'dont_merge_cookies': True}
            )
    
    def parse_category(self, response):
        """解析分類頁面，提取產品URL"""
        category_url = response.meta['category_url']
        category_name = category_url.split('/')[-1]
        
        self.logger.info(f"正在分析分類: {category_name}")
        
        # 使用多種選擇器嘗試獲取產品鏈接
        product_links = []
        
        # 嘗試方法1：針對產品卡片的鏈接
        links1 = response.css('div.grid-product__content a.grid-product__link::attr(href)').getall()
        if links1:
            product_links.extend(links1)
            self.logger.info(f"方法1找到 {len(links1)} 個產品鏈接")
        
        # 嘗試方法2：針對產品圖片的鏈接
        links2 = response.css('a.grid-product__image-link::attr(href)').getall()
        if links2:
            product_links.extend(links2)
            self.logger.info(f"方法2找到 {len(links2)} 個產品鏈接")
        
        # 嘗試方法3：尋找所有含有/products/的鏈接
        links3 = response.css('a[href*="/products/"]::attr(href)').getall()
        if links3:
            product_links.extend(links3)
            self.logger.info(f"方法3找到 {len(links3)} 個產品鏈接")
        
        # 如果沒有找到產品，可能網站結構有其他特點，嘗試提取頁面上所有鏈接
        if not product_links:
            self.logger.warning(f"未在 {category_name} 中找到產品鏈接，嘗試獲取所有鏈接")
            all_links = response.css('a::attr(href)').getall()
            for link in all_links:
                if '/products/' in link:
                    product_links.append(link)
            
            self.logger.info(f"通過所有鏈接過濾找到 {len(product_links)} 個產品鏈接")
        
        # 去重
        product_links = list(set(product_links))
        
        self.logger.info(f"在分類 {category_name} 中最終找到 {len(product_links)} 個產品鏈接")
        
        # 處理產品URL
        for link in product_links:
            # 確保是絕對URL
            product_url = response.urljoin(link)
            
            # 確保是產品URL並且不是已經收集過的
            if '/products/' in product_url and product_url not in self.collected_urls:
                self.collected_urls.add(product_url)
                
                # 提取產品名稱（從URL中）
                product_name = product_url.split('/')[-1].replace('-', ' ').title()
                
                # 保存到文件
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{product_url} # {product_name}\n")
                
                self.logger.info(f"收集到產品: {product_name}")
        
        # 檢查是否有下一頁
        next_page = response.css('a.pagination__next::attr(href), li.pagination-item--next a::attr(href), a[rel="next"]::attr(href), a:contains("Next")::attr(href)').get()
        if next_page:
            next_url = response.urljoin(next_page)
            self.logger.info(f"發現下一頁: {next_url}")
            
            # 添加延遲，避免過快請求
            time.sleep(1)
            
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_category,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': category_url
                },
                meta={'category_url': category_url, 'dont_merge_cookies': True}
            )
    
    def closed(self, reason):
        """爬蟲結束時執行，顯示統計信息"""
        self.logger.info(f"URL收集完成, 共收集了 {len(self.collected_urls)} 個產品URL")
        self.logger.info(f"結果已保存到: {self.output_file}") 