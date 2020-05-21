# -*- coding: utf-8 -*-
import re
import functools
import scrapy
from config import __config


ent = __config['reuters_search_entity']


class ReutersSpider(scrapy.Spider):
    name = 'reuters'
    allowed_domains = ['reuters.com']
    start_urls = [f'https://www.reuters.com/search/news?blob={ent}']

    def parse(self, response):
        """
        process start url responses
        """
        result = response.css('.search-result-title')
        timestamp = response.css('.search-result-timestamp::text').extract()
        for r, t in zip(result, timestamp):
            follow_link = r.css('a::attr(href)').extract_first()
            article_url = response.urljoin(follow_link)
            article_title = self.clean_up_title(r.css('a').extract_first())
            item = {'url': article_url, 'title': article_title, 'publish_date': t,
                         'source': 'reuters', 'original_key': ent}
            parse_article_dyn = functools.partial(self.parse_article, item=item)
            yield scrapy.Request(article_url, callback=parse_article_dyn)
    
    def parse_article(self, response, item):
        docs = response.css('.StandardArticleBody_body').xpath('//p/text()').extract()
        item['article'] = '\n'.join(docs)
        return item


    def clean_up_title(self, title):
        title = re.sub(r'^<[a-z0-9]{1,4} [A-Za-z0-9"/=]+>', '', title)
        title = re.sub(r'</?[a-z0-9]{1,4}>', '', title)
        return title