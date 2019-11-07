# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoautoparser.items import AvitoAutoparserItem
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/ufa/avtomobili?cd=1']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href| '
                                   '//a[@class="description-title-link js-item-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=AvitoAutoparserItem(), response=response)
        loader.add_xpath('photos', '//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_css('title', 'h1.title-info-title span.title-info-title-text::text')
        loader.add_xpath('price', '//meta[contains(@property, "product:price:amount")]/@content')
        loader.add_xpath('currency', '//meta[contains(@property, "product:price:currency")]/@content')
        loader.add_xpath('brand', '//div[@class="item-view-block"]//ul/li[1]/text()')
        loader.add_xpath('model', '///div[@class="item-view-block"]//ul/li[2]/text()')
        loader.add_xpath('year', '//div[@class="item-view-block"]//ul/li[5]/text()')
        loader.add_xpath('mileage', '//div[@class="item-view-block"]//ul/li[6]/text()')
        loader.add_xpath('transmission', '//div[@class="item-view-block"]//ul/li[13]/text()')
        loader.add_xpath('color', '//div[@class="item-view-block"]//ul/li[16]/text()')
        loader.add_css('link', 'link[rel="canonical"]::attr(href)')
        yield loader.load_item()
