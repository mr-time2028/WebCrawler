import scrapy
import json
from scrapy.crawler import CrawlerProcess    # for debug scrapy code



class ApiBanimodeSpider(scrapy.Spider):
    name = 'api_banimode'
    allowed_domains = ['banimode.com']
    start_urls = ['https://mobapi.banimode.com/api/v1/products?platform=desktop&filter[product_categories.id][eq]=623&filter[total_qty][gt]=0&page_size=24&page=1']


    def parse(self, response):
        products = json.loads(response.body.decode('utf-8'))

        # get category
        try:
            category = products["data"]["filters"]["categories"]["name"]
        except:
            category = "پوشاک"

        for product in products["data"]["data"]:
            
            # get colors 
            colors = []
            for color in product["all_colors_pwa"]:
                colors.append(color["name"])

            # get price, discount and discounted price
            try:
                price = product["product_price"]
                discount = product["product_specific_price"]["discount_percent"]
                discounted_price = product["product_specific_price"]["specific_price"]
            except:
                price = product["product_price"]
                discount = None
                discounted_price = None

            data = {
                "name": product["product_name"],
                "brand": product["product_manufacturer_name"],
                "category": category,
                "product_image": product["images"]["large_default"][0],
                "colors": ", ".join(colors),
                "price": price,
                "discount": discount,
                "discounted_price": discounted_price,
            }

            # json request to DjangoEcommerceApi project
            yield scrapy.Request(
                url='http://127.0.0.1:8000/api/products/',
                method='POST',
                body=json.dumps(data),
                headers={'Content-Type': 'application/json', 'Authorization':'Bearer <YOUR JWT>'},      # login and enter given JWT
                dont_filter=True
            )


        # pagination
        next_page_url = products["data"]["links"]["next"]
        if next_page_url is not None:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)



# for debug scrapy code
process = CrawlerProcess()
process.crawl(ApiBanimodeSpider)
process.start()