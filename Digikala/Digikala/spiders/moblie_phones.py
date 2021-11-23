import json
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

import re
from unidecode import unidecode   # convert persian numbers to english number


class MobilePhonesSpider(CrawlSpider):
    name = 'mobile_phones'
    allowed_domains = ['digikala.com']
    start_urls = ['https://www.digikala.com/search/category-mobile-phone']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=("//div[@class='c-product-box__title']/a")), callback='parse_item', follow=True),
    )


    def parse_item(self, response):

        # when a mobile phone have discount and disounted price, try to get them otherwise get the price.
        # maybe use of aggregation later so using int()
        try:
            discount = unidecode(response.xpath("(//div[@class='c-product__seller-price-off js-discount-value '])[2]/text()").get().strip())
            discounted_price = int(unidecode(response.xpath("//div[@class='c-product__seller-price-pure js-price-value']/text()").get().strip()).replace(",", ""))
            price = response.xpath("//div[@class='c-product__seller-price-prev js-rrp-price ']/text()").get()
        except:
            discount = None
            discounted_price = None
            price = response.xpath("//div[@class='c-product__seller-price-pure js-price-value']/text()").get()


        # get information of every mobile phone from https://www.digikala.com/search/category-mobile-phone
        # using strip() to remove spaces
        mobiles = {
            'title': response.xpath("//h1[@class='c-product__title']/text()").get().strip(),
            'product_image': response.xpath("//img[@class='js-gallery-img']/@data-src").get(),
            'category': response.xpath("//ul[@class='c-breadcrumb']/li[4]/a/span/text()").get(),
            'colors': ', '.join(response.xpath("//ul[@class='js-product-variants']/li/label/span[2]/text()").getall()),   # using getall() to gather data in list
            'product_features': ', '.join([s.replace(" ", "") for s in response.xpath("//div[@class='c-product__params js-is-expandable']/ul/li/span[2]/text()").getall()]),
            'star_rating': response.xpath("//div[@class='c-product__engagement-rating']/text()").get().strip(),
            'percent_rating': re.findall('\d+', response.xpath("//div[@class='c-product__user-suggestion-line']/text()").get().strip())[0] + "%",    # using regex to extract number
            'price': int(unidecode(price.strip()).replace(",", "")),
            'description': response.xpath("//div[@class='c-mask__text c-mask__text--product-summary js-mask__text']/text()").get().strip(),
            'stock_status': response.xpath("//span[@class='c-product__delivery-warehouse js-provider-main-title c-product__delivery-warehouse--no-lead-time']/text()").get().strip(),
            'discount': discount,
            'discounted_price': discounted_price,
        }

        # json request to DjangoEcommerceApi project
        yield scrapy.Request(
            url='http://127.0.0.1:8000/api/products/',
            method='POST',
            body=json.dumps(mobiles),
            headers={'Content-Type': 'application/json'},
            dont_filter=True
        )
