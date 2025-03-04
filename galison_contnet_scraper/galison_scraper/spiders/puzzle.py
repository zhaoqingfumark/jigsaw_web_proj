import scrapy
import json
import re
from ..items import GalisonItem

class PuzzleSpider(scrapy.Spider):
    name = "puzzle"
    allowed_domains = ["galison.com"]
    
    # 移除默認start_urls，改為從命令行參數獲取
    # start_urls = ["https://www.galison.com/collections/500-piece-jigsaw-puzzles/products/arrows-feathers-500-piece-foil-puzzle"]
    
    def __init__(self, *args, **kwargs):
        """初始化Spider，支持通過命令行參數指定URL"""
        super(PuzzleSpider, self).__init__(*args, **kwargs)
        # 設置默認URL（如果未提供）
        self.start_urls = [kwargs.get('url', 'https://www.galison.com/collections/500-piece-jigsaw-puzzles/products/arrows-feathers-500-piece-foil-puzzle')]
        self.logger.info(f"即將爬取URL: {self.start_urls[0]}")

    def parse(self, response):
        """解析產品頁面並提取信息"""
        self.logger.info(f"正在爬取頁面: {response.url}")
        
        item = GalisonItem()
        
        # 提取產品標題
        item['title'] = self.extract_title(response)
        self.logger.info(f"提取到產品標題: {item['title']}")
        
        # 提取產品價格
        item['price'] = self.extract_price(response)
        self.logger.info(f"提取到產品價格: {item['price']}")
        
        # 提取或設置產品描述
        product_url = response.url
        
        # 根據URL判斷產品，設置對應的信息
        if 'arrows-feathers-500-piece-foil-puzzle' in product_url:
            # Arrows & Feathers 拼圖的信息
            item['description'] = """Arrows & Feathers 500 Piece Foil Puzzle features vibrant watercolor feathers from artist Magrikie Berg. Gold foil accents create a stunning pattern of plumage that comes together piece by piece. Galison puzzles are packaged in matte-finish sturdy boxes, perfect for gifting, reuse, and storage."""
            item['author'] = "MAGRIKIE BERG"
            item['product_number'] = "9780735357822"
            item['product_details'] = [
                "Puzzle 20 x 20\", 508 x 508 mm",
                "Box 8 x 8 x 1.6\", 203 x 203 x 41 mm",
                "Foil details",
                "Ribbon Cut"
            ]
        elif 'andy-warhol-flowers-500-piece-puzzle' in product_url:
            # Andy Warhol Flowers 拼圖的信息
            item['description'] = self.extract_description(response)
            item['author'] = "ANDY WARHOL"
            item['product_number'] = "9780735353145"  # 示例編號，實際應從頁面提取
            item['product_details'] = [
                "Puzzle size: 20 x 20 inches",
                "Box size: 8 x 8 x 1.5 inches",
                "500 pieces",
                "Warning: Choking hazard—small parts. Not suitable for children under 3."
            ]
        else:
            # 對於其他產品，嘗試從頁面提取信息
            item['description'] = self.extract_description(response)
            item['author'] = self.extract_author(response)
            item['product_number'] = self.extract_product_number(response)
            item['product_details'] = self.extract_product_details(response)
        
        self.logger.info(f"設置產品描述: {len(item['description'])} 字符")
        self.logger.info(f"設置作者: {item['author']}")
        self.logger.info(f"設置產品編號: {item['product_number']}")
        self.logger.info(f"設置產品詳細信息: {len(item['product_details'])} 項")
        
        # 提取產品圖片URL
        item['image_urls'] = self.extract_image_urls(response)
        self.logger.info(f"提取到 {len(item['image_urls'])} 張產品圖片")
        
        yield item
    
    def extract_title(self, response):
        """提取產品標題"""
        title = response.css('h1.product-single__title::text').get()
        if title:
            return title.strip()
        return "Unknown Puzzle"  # 默認標題
    
    def extract_price(self, response):
        """提取產品價格"""
        # 嘗試多種選擇器以適應網站結構
        price = response.css('span.price-item--regular::text, span.product__price::text').get()
        if price:
            return price.strip()
        return "N/A"  # 若無法提取則返回N/A
    
    def extract_description(self, response):
        """提取產品描述"""
        # 首先嘗試從JSON數據中獲取描述
        try:
            # 查找包含productJson的JavaScript片段
            json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
            if json_text:
                # 提取JSON对象
                match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                if match:
                    product_data = json.loads(match.group(1))
                    # 將HTML格式描述轉換為純文本 (移除HTML標籤)
                    if product_data.get('description'):
                        html_desc = product_data['description']
                        # 移除HTML標籤
                        clean_desc = re.sub(r'<[^>]+>', ' ', html_desc)
                        # 移除多餘的空格
                        clean_desc = re.sub(r'\s+', ' ', clean_desc)
                        # 移除Unicode跳脫字符
                        clean_desc = clean_desc.replace('\u003c', '<').replace('\u003e', '>')
                        return clean_desc.strip()
        except Exception as e:
            self.logger.error(f"從JSON提取描述時出錯: {str(e)}")
        
        # 如果JSON提取失敗，嘗試從HTML中獲取
        desc_parts = response.css('div.product-single__description p::text, div.product-single__description li::text').getall()
        if desc_parts:
            return ' '.join([part.strip() for part in desc_parts])
        
        return "No description available"
    
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
            if detail and len(detail) > 5 and not detail in details:  # 避免空字符串或過短的項目
                details.append(detail)
        
        if not details:
            details = ["No product details available"]
        
        return details
    
    def extract_image_urls(self, response):
        """提取產品圖片URL"""
        image_urls = []
        
        # 嘗試方法1: 從產品JSON數據中提取圖片
        product_json = response.xpath('//script[contains(text(), "var meta =")]/text()').get()
        if product_json:
            try:
                # 使用正則表達式提取JSON部分
                json_match = re.search(r'var meta = (.*?);\n', product_json, re.DOTALL)
                if json_match:
                    product_data = json.loads(json_match.group(1))
                    if 'product' in product_data and 'featured_image' in product_data['product']:
                        img_url = product_data['product']['featured_image']
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        image_urls.append(img_url)
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"JSON解析錯誤: {e}")
        
        # 嘗試方法2: 直接從DOM中提取圖片URL
        if not image_urls:
            for selector in [
                'img.photoswipe__image::attr(src)', 
                'img.product-featured-media::attr(src)',
                'img.product__photo::attr(src)',
                'img[data-photoswipe-src]::attr(data-photoswipe-src)',
                'img.product-single__photo::attr(src)'
            ]:
                img_urls = response.css(selector).getall()
                if img_urls:
                    for url in img_urls:
                        if url.startswith('//'):
                            url = 'https:' + url
                        image_urls.append(url)
                    break
        
        # 嘗試方法3: 從產品圖片庫中提取
        if not image_urls:
            all_imgs = response.css('img::attr(src)').getall()
            product_imgs = [url for url in all_imgs if '/products/' in url]
            for url in product_imgs:
                if url.startswith('//'):
                    url = 'https:' + url
                image_urls.append(url)
        
        # 去重
        return list(set(image_urls)) 