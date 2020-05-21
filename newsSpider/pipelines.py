# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import data_pipeline.query_interface as dqi
import re
from datetime import datetime


class NewsSpiderPipeline:
    def process_item(self, item, spider):
        article = item['article']
        publish_date = self.parse_dates(item['publish_date'])
        print(publish_date)
        return item

    def parse_dates(self, date):
        dt = [*filter(lambda s: len(s) > 0, re.split(r'[\s,]', date))]
        dt = '-'.join(dt[:3])
        try:
            dt = datetime.strptime(dt, '%B-%d-%Y')
            return dt
        except Exception as e:
            dqi.utils.log(str(e))
        return datetime.strptime('1900-01-01', '%Y-%m-%d')
