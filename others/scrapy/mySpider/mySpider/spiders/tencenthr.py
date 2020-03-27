# -*- coding: utf-8 -*-
import scrapy
from mySpider.items import TencentItem


class TencenthrSpider(scrapy.Spider):
    name = 'tencenthr'
    allowed_domains = ['tencent.cn']
    start_urls = ['https://careers.tencent.com/search.html']

    def parse(self, response):
        tr_list = response.xpath("//table[@class='tablelist'/tr]")[1:-1] # 对列表切片, 去除首尾元素        
        for tr in tr_list:            
            # item = {}            
            item = TencentItem() # scrapy不推荐直接使用字典, 推荐使用mySpider.items中的Item对象                       
            item["title"] = tr.xpath("./td[1]/a/text()").extract_first() # 当前(tr)节点下的第一个td...
            item["position"] = tr.xpath("./td[2]/text()").extract_first()
            item["publish_date"] = tr.xpath("./td[5]/text()").extract_first()            
            yield item
        
        # 找到下一页的URL地址
        next_url = response.xpath("//a[@id='next']/@href").extract_first()
        if next_url and next_url != 'javascript:;':
            next_url = 'http://hr.tencent.com/' + next_url
            # yield一个Request对象, 可以将Request对象发送给引擎
            yield scrapy.Request(
                next_url,
                callback=self.parse # 指定提取数据的callback函数
            )
