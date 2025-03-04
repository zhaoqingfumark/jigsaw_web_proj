import scrapy

class GalisonItem(scrapy.Item):
    # 基本產品信息
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    product_number = scrapy.Field()
    product_details = scrapy.Field()
    
    # 圖片相關欄位 (Scrapy的圖片下載需要)
    image_urls = scrapy.Field()
    images = scrapy.Field() 