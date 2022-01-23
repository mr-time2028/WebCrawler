import scrapy
import json
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess      # for debug scrapy code


class MenApparelEpasazhSpider(CrawlSpider):
    name = 'men_apparel_epasazh'
    allowed_domains = ['epasazh.com']
    start_urls = ['https://epasazh.com/mens-apparel']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=("//div[@class='product-box-col']/a")), callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths=("//li[@class='next']/a"))),       # pagination
    )


    def parse_item(self, response):

        # when a mobile phone have discount and disounted price, try to get them otherwise get the price.
        # maybe use of aggregation later so using int() to convert price from str type to int type.
        try:
            discount = response.xpath("//span[@class='product-offer-tag pasazh-light-red-bg']/text()").get()
            discounted_price = int(response.xpath("//strong[@id='product-price']/text()").get().replace(',', ''))    # Error because int() cannot get ',' so we have to remove it from string.
            price = int(response.xpath("//span[@id='old-price']/text()").get().replace(',', ''))     # Error because int() cannot get ',' so we have to remove it from string.
        except:
            discount = None
            discounted_price = None
            price = int(response.xpath("//strong[@id='product-price']/text()").get().replace(',', ''))     # Error because int() cannot get ',' so we have to remove it from string.


        apparel = {
            'name': response.xpath("//h1[@id='product-title']/text()").get(),
            'product_image': response.xpath("//a[@class='quick_view'][1]/@href").get(),
            'brand': response.xpath("//div[@class='detail-holder']/h4/text()").get(),
            'category': response.xpath("//div[@id='simple-breadcrumb-holder']/ul/li[3]/a/span/text()").get(),
            'colors': ', '.join(response.xpath("//div[@class='spec-name-label lbl']/text()").getall()),     # using getall() to gather data in list and then using .join() to convert list to string.
            'price': price,
            'discount': discount,
            'discounted_price': discounted_price,
            'description': response.xpath("//div[@class='ws-break-space']/text()").get()
        }


        # json request to DjangoEcommerceApi project
        yield scrapy.Request(
            url='http://127.0.0.1:8000/api/products/',
            method='POST',
            body=json.dumps(apparel),
            headers={'Content-Type': 'application/json', 'Authorization':'Bearer <YOUR JWT>'},      # login and enter given JWT
            dont_filter=True
        )



# for debug scrapy code
process = CrawlerProcess()
process.crawl(MenApparelEpasazhSpider)
process.start()
