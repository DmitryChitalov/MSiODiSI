# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import scrapy


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


class AvitoAutoparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    brand = scrapy.Field(output_processor=Join())
    model = scrapy.Field(output_processor=Join())
    year = scrapy.Field(output_processor=Join())
    mileage = scrapy.Field(output_processor=Join())
    transmission = scrapy.Field(output_processor=Join())
    color = scrapy.Field(output_processor=Join())
    link = scrapy.Field(output_processor=TakeFirst())
