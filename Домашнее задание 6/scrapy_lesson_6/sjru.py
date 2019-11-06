# -*- coding: utf-8 -*-
import scrapy
from jobparser.items import JobparserItem

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
        # В этой версии приложения здесь лишь считываем данные о зарплате в виде списка. А обработка будет в пайплайн
        salary = response.css('span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] *::text').extract()
        site = 'superjob.ru'
        job_link = response.css('link[rel="canonical"]::attr(href)').extract_first()
        yield JobparserItem(name=job_name, min_salary=salary, max_salary=None, link=job_link, site=site)
