# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import re

class AvitoparserPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

class DataBasePipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_auto

    def process_item(self, item, spider):
        item['price'] = int(item['price'])
        item['brand'] = item['brand'].strip()
        try:
            item['year'] = int(re.sub(r'[^0-9]', '', item['year']))
        except:
            item['year'] = 'неизвестно'
        try:
            item['mileage'] = int(re.sub(r'[^0-9]', '', item['mileage']))
        except:
            item['mileage'] = 'неизвестно'
        item['model'] = item['model'].strip()
        item['transmission'] = item['transmission'].strip()
        item['color'] = item['color'].strip()
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
