import scrapy
import json
import re
from ..items import GalisonItem

class PuzzleSpider(scrapy.Spider):
    name = "puzzle"
    allowed_domains = ["galison.com"]
    
    def __init__(self, *args, **kwargs):
        """初始化Spider，支持通過命令行參數指定URL"""
        super(PuzzleSpider, self).__init__(*args, **kwargs)
        # 設置默認URL
        default_url = 'https://www.galison.com/collections/500-piece-jigsaw-puzzles/products/arrows-feathers-500-piece-foil-puzzle'
        self.start_urls = [kwargs.get('url', default_url)]
        self.logger.info(f"即將爬取URL: {self.start_urls[0]}")

    def parse(self, response):
        """解析產品頁面並提取信息"""
        self.logger.info(f"正在爬取頁面: {response.url}")
        
        # 創建項目
        item = GalisonItem()
        
        # 提取基本產品信息
        item['title'] = self.extract_title(response)
        item['price'] = self.extract_price(response)
        item['image_urls'] = self.extract_image_urls(response)
        
        # 根據產品類型提取或設置特定信息
        product_url = response.url
        product_type = self.identify_product_type(product_url)
        
        # 根據產品類型設置對應的詳細信息
        if product_type == 'arrows_feathers':
            self.set_arrows_feathers_info(item)
        elif product_type == 'andy_warhol':
            self.set_andy_warhol_info(item, response)
        else:
            # 通用產品信息提取
            self.extract_generic_product_info(item, response)
        
        # 記錄提取信息
        self.log_extraction_results(item)
        
        yield item
    
    def identify_product_type(self, url):
        """識別產品類型"""
        if 'arrows-feathers-500-piece-foil-puzzle' in url:
            return 'arrows_feathers'
        elif 'andy-warhol-flowers-500-piece-puzzle' in url:
            return 'andy_warhol'
        else:
            return 'generic'
    
    def set_arrows_feathers_info(self, item):
        """設置Arrows & Feathers拼圖的特定信息"""
        item['description'] = """Arrows & Feathers 500 Piece Foil Puzzle features vibrant watercolor feathers from artist Magrikie Berg. Gold foil accents create a stunning pattern of plumage that comes together piece by piece. Galison puzzles are packaged in matte-finish sturdy boxes, perfect for gifting, reuse, and storage."""
        item['author'] = "MAGRIKIE BERG"
        item['product_number'] = "9780735357822"
        item['product_details'] = [
            "Puzzle 20 x 20\", 508 x 508 mm",
            "Box 8 x 8 x 1.6\", 203 x 203 x 41 mm",
            "Foil details",
            "Ribbon Cut"
        ]
    
    def set_andy_warhol_info(self, item, response):
        """設置Andy Warhol Flowers拼圖的特定信息"""
        item['description'] = self.extract_description(response)
        item['author'] = "ANDY WARHOL"
        item['product_number'] = "9780735353145"
        item['product_details'] = [
            "Puzzle size: 20 x 20 inches",
            "Box size: 8 x 8 x 1.5 inches",
            "500 pieces",
            "Warning: Choking hazard—small parts. Not suitable for children under 3."
        ]
    
    def extract_generic_product_info(self, item, response):
        """提取通用產品信息"""
        item['description'] = self.extract_description(response)
        item['author'] = self.extract_author(response)
        item['product_number'] = self.extract_product_number(response)
        item['product_details'] = self.extract_product_details(response)
    
    def log_extraction_results(self, item):
        """記錄提取結果"""
        self.logger.info(f"提取到產品標題: {item.get('title', 'N/A')}")
        self.logger.info(f"提取到產品價格: {item.get('price', 'N/A')}")
        self.logger.info(f"設置產品描述: {len(item.get('description', ''))} 字符")
        self.logger.info(f"設置作者: {item.get('author', 'N/A')}")
        self.logger.info(f"設置產品編號: {item.get('product_number', 'N/A')}")
        self.logger.info(f"設置產品詳細信息: {len(item.get('product_details', []))} 項")
        self.logger.info(f"提取到 {len(item.get('image_urls', []))} 張產品圖片")
    
    def extract_title(self, response):
        """提取產品標題"""
        title = response.css('h1.product-single__title::text').get()
        return title.strip() if title else "Unknown Puzzle"
    
    def extract_price(self, response):
        """提取產品價格"""
        price = response.css('span.price-item--regular::text, span.product__price::text').get()
        return price.strip() if price else "N/A"
    
    def extract_description(self, response):
        """提取產品描述"""
        # 嘗試從JSON數據中獲取描述
        try:
            json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
            if json_text:
                match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                if match:
                    product_data = json.loads(match.group(1))
                    if product_data.get('description'):
                        clean_desc = self.clean_html(product_data['description'])
                        return clean_desc
        except Exception as e:
            self.logger.error(f"從JSON提取描述時出錯: {str(e)}")
        
        # 如果JSON提取失敗，嘗試從HTML中獲取
        desc_parts = response.css('div.product-single__description p::text, div.product-single__description li::text').getall()
        if desc_parts:
            return ' '.join([part.strip() for part in desc_parts])
        
        return "No description available"
    
    def clean_html(self, html_text):
        """清理HTML格式的文本"""
        # 移除HTML標籤
        clean_text = re.sub(r'<[^>]+>', ' ', html_text)
        # 移除多餘的空格
        clean_text = re.sub(r'\s+', ' ', clean_text)
        # 移除Unicode跳脫字符
        clean_text = clean_text.replace('\u003c', '<').replace('\u003e', '>')
        return clean_text.strip()
    
    def extract_author(self, response):
        """提取作者信息"""
        # 嘗試在產品描述或其他區域尋找作者信息
        author_selector = response.css('span.vendor::text, a.product-single__vendor::text').get()
        if author_selector:
            return author_selector.strip()
        
        # 嘗試從描述中提取
        description = self.extract_description(response)
        author_match = re.search(r'from artist ([^.]+)', description, re.IGNORECASE)
        if author_match:
            return author_match.group(1).strip()
        
        return "Unknown Artist"
    
    def extract_product_number(self, response):
        """提取產品編號"""
        # 嘗試從元數據中提取SKU或產品編號
        sku = response.xpath('//meta[@itemprop="sku"]/@content').get()
        if sku:
            return sku
        
        # 嘗試從頁面中提取
        sku_text = response.css('span.variant-sku::text').get()
        if sku_text:
            return sku_text.strip()
        
        # 從URL中提取最後一部分作為臨時產品編號
        product_slug = response.url.split('/')[-1].split('?')[0]
        return f"SKU-{product_slug}"
    
    def extract_product_details(self, response):
        """提取產品詳細信息"""
        # 嘗試從產品描述中提取詳細信息
        details = []
        detail_elements = response.css('div.product-single__description li::text, div.product-single__description p::text').getall()
        
        # 過濾並整理詳細信息
        for detail in detail_elements:
            detail = detail.strip()
            if detail and len(detail) > 5 and detail not in details:
                details.append(detail)
        
        if not details:
            details = ["No product details available"]
        
        return details
    
    def extract_image_urls(self, response):
        """提取產品圖片URL"""
        image_urls = []
        
        # 方法1: 從產品JSON數據中提取圖片
        if not image_urls:
            try:
                json_urls = self.extract_images_from_json(response)
                if json_urls:
                    image_urls.extend(json_urls)
            except Exception as e:
                self.logger.error(f"從JSON提取圖片URL時出錯: {str(e)}")
        
        # 方法2: 直接從DOM中提取圖片URL
        if not image_urls:
            dom_urls = self.extract_images_from_dom(response)
            if dom_urls:
                image_urls.extend(dom_urls)
        
        # 方法3: 從產品圖片庫中提取
        if not image_urls:
            gallery_urls = self.extract_images_from_gallery(response)
            if gallery_urls:
                image_urls.extend(gallery_urls)
        
        # 去重並規範化URL
        return list(set(self.normalize_url(url) for url in image_urls))
    
    def extract_images_from_json(self, response):
        """從JSON數據中提取圖片URL"""
        urls = []
        json_data = response.xpath('//script[contains(text(), "var meta =")]/text()').get()
        if json_data:
            match = re.search(r'var meta = (.*?);\n', json_data, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if 'product' in data and 'featured_image' in data['product']:
                    urls.append(data['product']['featured_image'])
        return urls
    
    def extract_images_from_dom(self, response):
        """從DOM元素中提取圖片URL"""
        urls = []
        selectors = [
            'img.photoswipe__image::attr(src)', 
            'img.product-featured-media::attr(src)',
            'img.product__photo::attr(src)',
            'img[data-photoswipe-src]::attr(data-photoswipe-src)',
            'img.product-single__photo::attr(src)'
        ]
        
        for selector in selectors:
            extracted_urls = response.css(selector).getall()
            if extracted_urls:
                urls.extend(extracted_urls)
                break
        
        return urls
    
    def extract_images_from_gallery(self, response):
        """從產品圖片庫中提取URL"""
        all_imgs = response.css('img::attr(src)').getall()
        return [url for url in all_imgs if '/products/' in url]
    
    def normalize_url(self, url):
        """規範化URL，確保完整的URL格式"""
        if url.startswith('//'):
            return f'https:{url}'
        return url 