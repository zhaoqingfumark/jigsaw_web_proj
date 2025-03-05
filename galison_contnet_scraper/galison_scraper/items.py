import scrapy

class GalisonItem(scrapy.Item):
    # Basic product information
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    product_number = scrapy.Field()
    product_id = scrapy.Field()  # 用于图片存储的产品ID标识
    product_details = scrapy.Field()
    
    # Image related fields (required for Scrapy's image download)
    image_urls = scrapy.Field()
    images = scrapy.Field() 