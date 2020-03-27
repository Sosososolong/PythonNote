# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
logger = logging.getLogger(__name__)

# from pymongo import MongoClient
# client = MongoClient()
# collection = client["tencent"]["hr"]


class MyspiderPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'itcast':
            logger.warning(item)  # 2020-03-15 13:48:13 [mySpider.pipelines] WARNING: {'name': '袁老师', 'title': '高级讲师'}
        return item

class MyspiderPipelineTencent(object):
    def process_item(self, item, spider):        
        if spider.name == 'tencenthr':
            collection.insert(dict(item))
        return item

class MyspiderPipelineTieba:
    def process_item(self, item, spider):
        if spider.name == 'tieba':
            print(item)
