# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import random

class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/mo/q/moindex/feedlist?load_type=2&need_hot_topic=1']

    def parse(self, response):
        # res = "\u8fd9\u662f\u6768\u9896\uff1f\u6211\u662f\u4e0d\u662f\u9519\u8fc7\u4e86\u4ec0\u4e48".decode("utf8")
        datas = json.loads(response.text)['data']['thread_personalized'] # 列表
        for data in datas:            
            print(' ')
            item = {}
            item['forum_name'] = data['thread_info']['forum_name']            
            item['tid'] = data['tid']                               
            item['title'] = data['thread_info']['title']            
            item['user_id'] = data['thread_info']['user_id']            
            item['abstract'] = data['thread_info']['abstract']            
            item['img'] = [{'small_pic': i['big_pic'], 'big_pic':i['big_pic']} for i in data['thread_info']['media'] if i['type']=='pic']            
            
            yield item
        
        yield scrapy.Request(
            self.start_urls[0] + '&ran=' + str(random.randint(0,50)),
            callback=self.parse,            
        )
    
