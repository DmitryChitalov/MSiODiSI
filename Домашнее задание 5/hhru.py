# -*- coding: utf-8 -*-
import scrapy
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    search_str = 'Python'
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=' + search_str +
                  '&showClusters=false']

    def parse(self, response):  # Точка входа, отсюда начинаем работать
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        if not next_page:
            pass
        else:
            yield response.follow(next_page, callback=self.parse)  # Переходим на следующую страницу и возвращаемся

        vacansy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)'
        ).extract()  # Извлекаем ссылки на все вакансии

        for link in vacansy:
            yield response.follow(link, self.vacansy_parse)  # Переходим на страницы вакансий

    def vacansy_parse(self, response):  # Собираем информацию со страницы
        job_name = response.css('div.vacancy-title h1.header::text').extract_first().strip()
        salary_min = response.css('meta[itemprop="minValue"]::attr(content)').extract_first()
        if not salary_min:
            salary_min = None
        salary_max = response.css('meta[itemprop="maxValue"]::attr(content)').extract_first()
        if not salary_max:
            salary_max = None
        site = 'hh.ru'
        job_link = response.css('div[itemscope="itemscope"] meta[itemprop="url"]::attr(content)').extract_first()
        yield JobparserItem(name=job_name, min_salary=salary_min, max_salary=salary_max, link=job_link, site=site)
