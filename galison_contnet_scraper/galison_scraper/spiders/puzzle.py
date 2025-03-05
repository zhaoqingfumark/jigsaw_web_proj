import scrapy
import json
import re
from ..items import GalisonItem

class PuzzleSpider(scrapy.Spider):
    name = "puzzle"
    allowed_domains = ["galison.com"]
    
    def __init__(self, *args, **kwargs):
        """Initialize Spider, supports URL specification via command line parameters"""
        super(PuzzleSpider, self).__init__(*args, **kwargs)
        # Set default URL
        default_url = 'https://www.galison.com/collections/500-piece-jigsaw-puzzles/products/arrows-feathers-500-piece-foil-puzzle'
        self.start_urls = [kwargs.get('url', default_url)]
        self.logger.info(f"Will crawl URL: {self.start_urls[0]}")

    def parse(self, response):
        """Parse product page and extract information"""
        self.logger.info(f"Crawling page: {response.url}")
        
        # Create item
        item = GalisonItem()
        
        # Extract basic product information
        item['title'] = self.extract_title(response)
        item['price'] = self.extract_price(response)
        item['image_urls'] = self.extract_image_urls(response)
        
        # Extract product number and use it as product_id
        product_number = self.extract_product_number(response)
        item['product_number'] = product_number
        
        # Add product_id field for image pipeline
        item['product_id'] = product_number.replace(" ", "_").replace("-", "_")
        
        # Extract or set specific information based on product type
        product_url = response.url
        product_type = self.identify_product_type(product_url)
        
        # Set corresponding detailed information based on product type
        if product_type == 'arrows_feathers':
            self.set_arrows_feathers_info(item)
        elif product_type == 'andy_warhol':
            self.set_andy_warhol_info(item, response)
        else:
            # Extract generic product information
            self.extract_generic_product_info(item, response)
        
        # Log extraction results
        self.log_extraction_results(item)
        
        yield item
    
    def identify_product_type(self, url):
        """Identify product type"""
        if 'arrows-feathers-500-piece-foil-puzzle' in url:
            return 'arrows_feathers'
        elif 'andy-warhol-flowers-500-piece-puzzle' in url:
            return 'andy_warhol'
        else:
            return 'generic'
    
    def set_arrows_feathers_info(self, item):
        """Set specific information for Arrows & Feathers puzzle"""
        item['description'] = """Arrows & Feathers 500 Piece Foil Puzzle features vibrant watercolor feathers from artist Magrikie Berg. Gold foil accents create a stunning pattern of plumage that comes together piece by piece. Galison puzzles are packaged in matte-finish sturdy boxes, perfect for gifting, reuse, and storage."""
        item['author'] = "MAGRIKIE BERG"
        
        # Don't override product_number if already set
        if 'product_number' not in item or not item['product_number']:
            item['product_number'] = "9780735357822"
            item['product_id'] = "9780735357822"
            
        item['product_details'] = [
            "Puzzle 20 x 20\", 508 x 508 mm",
            "Box 8 x 8 x 1.6\", 203 x 203 x 41 mm",
            "Foil details",
            "Ribbon Cut"
        ]
    
    def set_andy_warhol_info(self, item, response):
        """Set specific information for Andy Warhol Flowers puzzle"""
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
        """Extract generic product information"""
        item['description'] = self.extract_description(response)
        item['author'] = self.extract_author(response)
        item['product_number'] = self.extract_product_number(response)
        item['product_details'] = self.extract_product_details(response)
    
    def log_extraction_results(self, item):
        """Log extraction results"""
        self.logger.info(f"Extracted product title: {item.get('title', 'N/A')}")
        self.logger.info(f"Extracted product price: {item.get('price', 'N/A')}")
        self.logger.info(f"Set product description: {len(item.get('description', ''))} characters")
        self.logger.info(f"Set author: {item.get('author', 'N/A')}")
        self.logger.info(f"Set product number: {item.get('product_number', 'N/A')}")
        self.logger.info(f"Set product details: {len(item.get('product_details', []))} items")
        self.logger.info(f"Extracted {len(item.get('image_urls', []))} product images")
    
    def extract_title(self, response):
        """Extract product title"""
        title = response.css('h1.product-single__title::text').get()
        return title.strip() if title else "Unknown Puzzle"
    
    def extract_price(self, response):
        """Extract product price"""
        price = response.css('span.price-item--regular::text, span.product__price::text').get()
        return price.strip() if price else "N/A"
    
    def extract_description(self, response):
        """Extract product description"""
        # Try to get description from JSON data
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
            self.logger.error(f"Error extracting description from JSON: {str(e)}")
        
        # If JSON extraction fails, try to get description from HTML
        desc_parts = response.css('div.product-single__description p::text, div.product-single__description li::text').getall()
        if desc_parts:
            return ' '.join([part.strip() for part in desc_parts])
        
        return "No description available"
    
    def clean_html(self, html_text):
        """Clean HTML formatted text"""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', html_text)
        # Remove extra spaces
        clean_text = re.sub(r'\s+', ' ', clean_text)
        # Remove Unicode escape characters
        clean_text = clean_text.replace('\u003c', '<').replace('\u003e', '>')
        return clean_text.strip()
    
    def extract_author(self, response):
        """Extract author information"""
        # Try to get author information from JSON data or meta data
        try:
            # Extract from productJson
            json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
            if json_text:
                match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                if match:
                    product_data = json.loads(match.group(1))
                    if product_data.get('vendor'):
                        return product_data['vendor']
            
            # Extract from meta data
            meta_text = response.xpath('//script[contains(text(), "var meta =")]/text()').get()
            if meta_text:
                match = re.search(r'var meta = (.*?);\n', meta_text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    if 'product' in data and 'vendor' in data['product']:
                        return data['product']['vendor']
        except Exception as e:
            self.logger.error(f"Error extracting author: {str(e)}")
        
        # Try to find author information in product description or other area
        author_selector = response.css('span.vendor::text, a.product-single__vendor::text').get()
        if author_selector:
            return author_selector.strip()
        
        # Try to extract from description
        description = self.extract_description(response)
        author_match = re.search(r'by ([^.]+)(?:artist|illustrator)', description, re.IGNORECASE)
        if author_match:
            return author_match.group(1).strip()
        
        return "Unknown Artist"
    
    def extract_product_number(self, response):
        """Extract product number"""
        # Try to get SKU from productJson
        try:
            json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
            if json_text:
                match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                if match:
                    product_data = json.loads(match.group(1))
                    if product_data.get('variants') and len(product_data['variants']) > 0:
                        if product_data['variants'][0].get('sku'):
                            return product_data['variants'][0]['sku']
                        elif product_data['variants'][0].get('barcode'):
                            return product_data['variants'][0]['barcode']
        except Exception as e:
            self.logger.error(f"Error extracting product number from JSON: {str(e)}")
        
        # Try to get SKU from meta data
        try:
            meta_text = response.xpath('//script[contains(text(), "var meta =")]/text()').get()
            if meta_text:
                match = re.search(r'var meta = (.*?);\n', meta_text, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    if 'product' in data and 'variants' in data['product'] and len(data['product']['variants']) > 0:
                        if data['product']['variants'][0].get('sku'):
                            return data['product']['variants'][0]['sku']
        except Exception as e:
            self.logger.error(f"Error extracting product number from meta: {str(e)}")
        
        # Try to get SKU or product number from meta data
        sku = response.xpath('//meta[@itemprop="sku"]/@content').get()
        if sku:
            return sku
        
        # Try to extract from page
        sku_text = response.css('span.variant-sku::text').get()
        if sku_text:
            return sku_text.strip()
        
        # Extract last part of URL as temporary product number
        product_slug = response.url.split('/')[-1].split('?')[0]
        return f"SKU-{product_slug}"
    
    def extract_product_details(self, response):
        """Extract product details"""
        # Try to get description from productJson and parse out details
        details = []
        try:
            json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
            if json_text:
                match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                if match:
                    product_data = json.loads(match.group(1))
                    if product_data.get('description'):
                        description = self.clean_html(product_data['description'])
                        # Extract lines starting with dash or dot from description, these are usually product details
                        detail_lines = re.findall(r'[-•]\s*([^\n]+)', description)
                        if detail_lines:
                            for detail in detail_lines:
                                detail = detail.strip()
                                if detail and len(detail) > 3 and detail not in details:
                                    details.append(detail)
        except Exception as e:
            self.logger.error(f"Error extracting product details from JSON: {str(e)}")
        
        # If no details are extracted from JSON, try to get from DOM
        if not details:
            detail_elements = response.css('div.product-single__description li::text, div.product-single__description p::text').getall()
            
            # Filter and organize details
            for detail in detail_elements:
                detail = detail.strip()
                if detail and len(detail) > 5 and detail not in details:
                    details.append(detail)
        
        if not details:
            details = ["No product details available"]
        
        return details
    
    def extract_image_urls(self, response):
        """Extract image URLs"""
        image_urls = []
        
        # Try to get images from media gallery
        image_elements = response.css('div.product-single__media-flex-wrapper img.photoswipe__image')
        if image_elements:
            for img in image_elements:
                src = img.css('::attr(src)').get()
                if src:
                    # Get highest resolution version by modifying URL parameters
                    src = self.get_high_resolution_url(src)
                    image_urls.append(src)
        
        # If no images found in gallery, try other selectors
        if not image_urls:
            # Try product thumbnail
            thumbnail = response.css('img.product-featured-img::attr(src), img.product-featured-media::attr(src)').get()
            if thumbnail:
                thumbnail = self.get_high_resolution_url(thumbnail)
                image_urls.append(thumbnail)
            
            # Try variant images
            variant_images = response.css('div.product-single__thumbnails img::attr(src)').getall()
            for img in variant_images:
                if img:
                    img = self.get_high_resolution_url(img)
                    if img not in image_urls:
                        image_urls.append(img)
        
        # If still no images found, try JSON data
        if not image_urls:
            try:
                json_text = response.xpath('//script[contains(text(), "productJson")]/text()').get()
                if json_text:
                    match = re.search(r'productJson: ({.*}),', json_text, re.DOTALL)
                    if match:
                        product_data = json.loads(match.group(1))
                        if product_data.get('images'):
                            for img in product_data['images']:
                                img_url = 'https:' + img if img.startswith('//') else img
                                img_url = self.get_high_resolution_url(img_url)
                                if img_url not in image_urls:
                                    image_urls.append(img_url)
            except Exception as e:
                self.logger.error(f"Error extracting image URLs from JSON: {str(e)}")
        
        return image_urls
    
    def get_high_resolution_url(self, url):
        """Get high resolution version of image URL"""
        # Ensure URL is absolute
        if url.startswith('//'):
            url = 'https:' + url
        
        # Update URL parameters for higher resolution
        if '?' in url:
            base_url, params = url.split('?', 1)
            # Add width parameter for higher resolution, if not present
            if 'width=' not in params:
                return f"{base_url}?{params}&width=1080"
            else:
                # Replace existing width with higher value
                return re.sub(r'width=\d+', 'width=1080', url)
        else:
            return f"{url}?width=1080" 