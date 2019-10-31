# -*- coding: utf-8 -*-
import scrapy
from jobparser.items import JobparserItem
import re

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    search_str = 'Python'
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=' + search_str +
                  '&geo%5Bc%5D%5B0%5D=1']

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        if not next_page:
            pass
        else:
            yield response.follow(next_page, callback=self.parse)

        vacansy = response.css(
            'div.f-test-vacancy-item a[target="_blank"]::attr(href)').extract()

        for link in vacansy:
            yield response.follow(link, self.vacansy_parse)  # Переходим на страницы вакансий

    def vacansy_parse(self, response):
        job_name = response.css('div._3MVeX h1::text').extract_first().strip()
        salary = response.css('span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] *::text').extract()
        salary = str(''.join(salary))
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
        site = 'superjob.ru'
        job_link = response.css('link[rel="canonical"]::attr(href)').extract_first()
        yield JobparserItem(name=job_name, min_salary=salary_min, max_salary=salary_max, link=job_link, site=site)
