# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import re

class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_vacansy

    def process_item(self, item, spider):  # Сюда попадает item
        # Обработаем информацию о зарплате
        if spider.name == 'hhru':
            item['name'] = str(item['name'][1])
            item["min_salary"] = item["min_salary"][len(item["min_salary"]) - 1]
            item["max_salary"] = item["max_salary"][len(item["max_salary"]) - 1]
            item['link'] = str(item['link'][0])
            item['site'] = str(item['site'][0])
            '''
            if item['min_salary']:
                item['min_salary'] = int(item['min_salary'])
            if item['max_salary']:
                item['max_salary'] = int(item['max_salary'])
            '''
        elif spider.name == 'sjru':
            salary = str(''.join(item['min_salary'])).strip()
            salary = salary.replace(u'\xa0', u'')
            if '—' in salary:
                salary_min = salary.split('—')[0]
                salary_min = re.sub(r'[^0-9]', '', salary_min)
                salary_max = salary.split('—')[1]
                salary_max = re.sub(r'[^0-9]', '', salary_max)
                salary_min = int(salary_min)
                salary_max = int(salary_max)
            elif 'от' in salary:
                salary_min = salary[2:]
                salary_min = re.sub(r'[^0-9]', '', salary_min)
                salary_min = int(salary_min)
                salary_max = None
            elif 'договорённости' in salary:
                salary_min = None
                salary_max = None
            elif 'до' in salary:
                salary_min = None
                salary_max = salary[2:]
                salary_max = re.sub(r'[^0-9]', '', salary_max)
                salary_max = int(salary_max)
            else:
                salary_min = int(re.sub(r'[^0-9]', '', salary))
                salary_max = int(re.sub(r'[^0-9]', '', salary))
            item['min_salary'] = salary_min
            item['max_salary'] = salary_max

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

