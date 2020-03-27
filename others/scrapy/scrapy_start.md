# 入门

## 从零开始创建一个简单的项目

1. pip直接安装scrapy, 依赖的库也会直接安装上
    - `pip install scrapy`, 安装完成后, xxx/python_virtualenv/Scripts/ 目录下就会出现scrapy.exe文件, 全局可用
2. 创建一个scrapy项目
    - `scrapy startproject mySpider`
    - 目录层级

        ```python
            + mySpider # 项目根目录
                + mySpider
                    + __pycache__
                    + spiders
                        + __pycache__
                        + __init__.py
                        + itcast.py
                    + __init__.py
                    + items.py
                    + middlewares.py
                    + pipelines.py
                    + settings.py
                + scrapy.cfg
        ```

3. 进入项目根目录 mySpider/, 生成一个爬虫
    - `scrapy genspider itcast "itcast.cn"`

        ```python
        import scrapy

        class ItcastSpider(scrapy.Spider):
            name = 'itcast'
            allowed_domains = ['itcast.cn']
            # 初始url, scrapy引擎会根据此url去爬取数据, 然后交给parse()方法
            start_urls = ['http://www.itcast.cn/channel/teacher.shtml']

            def parse(self, response):
                parse
        ```

4. 提取数据
    - 完善spider, 使用xpath等方法
    - 打开mySpider/mySpider/spiders/itcast.py文件, ItcastSpider的name是爬虫名称, start_urls中是爬虫最开始请求的地址, parse()方法中处理爬虫结果, 补充parse()方法

        ```python
        def parse(self, response):
            # ret1 = response.xpath("//div[@class='tea_con']//h3/text()").extract()
            # print(ret1)

            li_list = response.xpath("//div[@class='tea_con']//li")
            for li in li_list:
                item = {}
                item["name"] = li.xpath(".//h3/text()").extract_first()
                item["title"] = li.xpath(".//h4/text()").extract_first()
                # print(item)

                yield item  # 将item传入pipline(scrapy中存储数据的地方), 需要将settings.py中的**ITEM_PIPELINES**项的注释去掉才能开启**piplines**
        ```

5. 配置piplines
    - 打开settings.py, 去掉`ITEM_PIPELINES`的注释
    - 现在默认情况下只有一个**pipline:** `mySpider.pipelines.MyspiderPipeline`, 即piplines.py中的MyspiderPipline类, 如果希望添加其他的pipline, 就在`pipline.py`中添加一个类即可, 入`class MyspiderPipline1`, 然后再配置文件中, 添加此新建的pipline即可

        ```python
        ITEM_PIPELINES = {
        'mySpider.pipelines.MyspiderPipeline': 300,
        # 每个pipline名称作为键, 后面的值(300, 302)表示该pipline的权重(也就是说爬虫传过来的数据会先经过值小的pipline, 值小的pipline中的业务逻辑会先执行)
        'mySpider.pipelines.MyspiderPipeline1': 302,
        }
        ```

6. 启动爬虫
    - `scrapy crawl itcast`
    - 修改settings.py, 将日志输出的级别改为warning以上: `LOG_LEVEL = 'WARNING'`

7. 保存数据
    - pipeline中保存数据

        ```python
        class MyspiderPipeline(object):
            def process_item(self, item, spider):  # spider就是爬虫类(ItcastSpider)的实例
                return item
        ```

## logging模块的使用

- logging并不是scrapy专属的模块, 只不过scrapy提供了一个总的配置文件`settings.py`, 在此文件中我们可以按照scrapy的要求去配置logging模块

### 在scrapy中使用logging

1. 配置logging: 在settings.py中添加`LOG_LEVEL = 'WARNING'`将日志的输出级别改为warning
2. 日志操作
    - 需要引入logging模块`import logging`, 输出一个warning登记的日志信息: `logging.warning( )`
        - 使用logging模块在控制台输出信息和print()方法类似, 但是logging默认还会输出当前输出的时间, 信息的重要等级(例如info,warning,error), 最重要的是, logging模块可以将需要输出的信息持久化保存到本地磁盘中, 方便随时查看

    - 基于logging更优化的日志处理方式, `logger = logging.getLogger(__name__)` 通过logging得到的logger实例在输出日志的时候, 不但使用的方法名称还是一样的, 还会输出当前输出来自于哪个文件, 这样就能方便的在代码中找到当前输出的位置
        - Python中, 模块(.py)有自己的一些內建变量, 比如`__name__`, 它的值有两种情况
            - 当当前模块由另一个模块调用的时候, 当前模块中的`__name__ == 当前模块名`
            - 当Python解析器直接执行当前模块的时候, `__name__ == '__main__'`

        - 代码

            ```python
            import logging
            logger = logging.getLogger(__name__)
            class MyspiderPipeline(object):
                def process_item(self, item, spider):
                    if spider.name == 'itcast':
                        logger.warning(item)  # 2020-03-15 13:48:13 [mySpider.pipelines] WARNING: {'name': '袁老师', 'title': '高级讲师'}
                    return item
            ```

    - 保存到本地文件中
        - settings.py中添加配置项`LOG_FILE = './log.txt'`, 通过指定**日志文件名称**的方式可以将输出信息(日志)输出到指定文件, 这里的相对路径是相对于项目的根目录而言, 日志文件位置如下:

            ```python
            + mySpider
                + mySpider
                    + ...
                + log.txt
                + scrapy.cfg
            ```

### 在普通的python模块中使用logging

- 除了在scrapy中, 普通的python模块也可以使用logging模块记录日志, 只不过需要自己配置一下输出格式即可

    ```python
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s '
        'thread: %(threadName)s output msg: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
        # filename='./myapp.log',
        # filemode='w'
    )

    logger = logging.getLogger(__name__)

    if __name__ == '__main__':
        logger.info("this is a info log")
        logger.info("this is a info log 2")


    # 假设上面的Python模块是`my_logger.py`, 当任何一个其他模块需要使用日志功能的时候, 导入上面的logger即可:
    from my_logger.py import logger
    logger.warning("this is a warning log")
    ```

## 怎么主动发送请求(翻页构建下一页的url后, 怎么把新的url地址传递给scrapy引擎)

1. `scrapy genspider tencenthr tencent.cn`新建一个爬虫`tencenthr`, 修改爬虫文件`tencenthr.py`

    ```python
    def parse(self, response):
            tr_list = response.xpath("//table[@class='tablelist'/tr]")[1:-1] # 对列表切片, 去除首尾元素
            for tr in tr_list:
                item = {}
                item["title"] = tr.xpath("./td[1]/a/text()").extract_first() # 当前(tr)节点下的第一个td...
                item["position"] = tr.xpath("./td[2]/text()").extract_first()
                item["position"] = tr.xpath("./td[5]/text()").extract_first()
                yield item

            # 找到下一页的URL地址
            next_url = response.xpath("//a[@id='next']/@href").extract_first()
            if next_url != 'javascript:;':
                next_url = 'http://hr.tencent.com/' + next_url
                # yield一个Request对象, 可以将Request对象发送给引擎
                yield scrapy.Request(
                    next_url,
                    callback=self.parse # 指定提取数据的callback函数, 这里指定当前函数
                )
    ```

2. settings.py中可以设置USER_AGENT: `USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'`

3. piplines中将数据保存到MongoDB中

    ```python
    from pymongo import MongoClient
    client = MongoClient()
    collection = client["tencent"]["hr"]

    class MyspiderPipelineTencent(object): # 记得将此pipline在settings.py中注册一下
        def process_item(self, item, spider):
            if spider.name == 'tencenthr':
                collection.insert(item)
                return item
    ```

## item对象

1. 在项目的`items.py`文件中, 添加一个item类(继承自scrapy.Item)

    ```python
    # items.py

    class TencentItem(scrapy.Item):
        # define the fields for your item here like:
        # name = scrapy.Field()
        title = scrapy.Field()
        position = scrapy.Field()
        publish_date = scrapy.Field()
    ```

2. 之前在构建一条传入pipline的数据的时候用的是字典, 这里使用item对象

    ```python
    # tencenthr.py 爬虫
    from mySpider.items import TencentItem

    for tr in tr_list:
        # item = {}
        item = TencentItem() # scrapy不推荐直接使用字典, 推荐使用mySpider.items中的Item对象
        item["title"] = tr.xpath("./td[1]/a/text()").extract_first() # 当前(tr)节点下的第一个td...
        item["position"] = tr.xpath("./td[2]/text()").extract_first()
        item["publish_date"] = tr.xpath("./td[5]/text()").extract_first()
        yield item
    ```

3. 在pipline中获取到上面的item对象后, 如果需要的是字典类型那么就需要将item对象转换成字典类型

```python
class MyspiderPipelineTencent(object):
    def process_item(self, item, spider):
        if spider.name == 'tencenthr':
            collection.insert(dict(item)) # insert()方法接收一个字典类型
        return item
```

## 数据有详情页的时候(爬取详情)

1. 爬虫中代码

    ```python
        tr_list = response.xpath("xxx")
        for tr in tr_list:
            item = YangguangItem()
            item["title"] = tr.xpath("xxx")
            item["href"] = tr.xpath("xxx")
            item["publish_date"] = tr.xpath("xxx")

            # 每次获取了一条信息, 再爬取当前信息的详情页(通过详情url, 发送新的请求给scrapy引擎, yield Request对象即可)
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail, # 处理详情页的逻辑跟当前函数不符, 需要重新定义一个函数专门提取详情页数据
                # meta参数的作用是将当前函数中的数据传递到另一个函数中(parse_detail)中
                # 这里的item传给下面的方法后, 会紧接着接收其他数据, item就会改变了, 为了是这里的item的改变不影响下面的item的数据(这里是不影响的, 这里使用deepcopy只是说明影响的情况下的应对方式), 可以使用deepcopy(), from copy import deepcopy
                meta={"item":deepcopy(item)}
            )

        # 翻页 使用">"判断是否有下一页
        next_url = response.xpath("//a[text()='>']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(
                next_url,
                callback=self.parse
            )

    def parse_detail(self, response){ # 处理详情页
        item = response.meta["item"]
        # 给item添加详情数据
        item["content"] = response.xpath("//div[@class='c1 text14_2']//text()").extract() # 结果可能不止一个的话就使用extract()返回一个集合, 而不是extract_first()
        item["content_img"] = response.xpath("//div[@class='c1 text14_2']//img/@src").extract()
        item["content_img"] = ["http://wz.sun0769.com" + i for i in item["content_img"]]
        # yield出去给pipline
        yield item
    }

    # pipline 中处理爬虫中返回的数据
    import re
    class YangguangPipline(object):
        def process_item(self, item, spider):
            # item["content"] 是一个字符串列表(每一个项的详情内容有多条)
            item["content"] = self.process_content(item["content"])
            return item

        def process_content(self, content):
            content = [re.sub(r"\xa0|\s", "", i) for i in content]
            content = [i for i in content if len(i)>0] # 取出列表中的空字符串
            return content
    ```

## scrapy的debug信息

- [scrapy.utils.log] INFO: Overridden settings: 自己设置的setting信息
- [scrapy.middleware] INFO: Enabled extension: 启动的扩展, 默认有一堆
- [scrapy.middleware] INFO: Enabled downloader middlewares: 启动的下载中间件, 默认有一堆
- [scrapy.middleware] INFO: Enabled spider middlewares: 启动的爬虫中间件, 默认有一堆
- [scrapy.middleware] INFO: Enabled item piplines: 启动的管道
- [scrapy.extensions.talnet] INFO: DEBUG: 爬虫运行的时候能够用talnet命令对爬虫做一些控制,比如暂停等
- [scrapy.statscollectors] INFO: Dumping Scrapy stats: 爬虫结束的时候的一些统计信息, 比如请求响应数量等
- [scrapy.core.scraper] DEBUG: Scraped from <200 `http://wz.sun0769.com/html/question/201707/340346.shtml`>{'content': ...}: 每次`yield item`的时候回提示item的内容以及这个item来自的URL地址

## scrapy shell

- 在终端输入命令 `scrapy shell URL`, 就会进入python或者ipython终端, 并进入爬虫调试模式, 在此环境中, 可以查看诸多对象(终端中会提示Available Scrapy objects)的成员属性或者方法, 也可以调试xpath()

```shell
> response.url
    'http://www.itcast.cn/channel/teacher.shtml'
> response.request.url
    'http://www.itcast.cn/channel/teacher.shtml'
> response.body: 响应体, 也就是html代码, 默认byte类型

```

## settings配置文件

- 当我们自定义一些配置项的时候, 如配置一个MongoDB的服务器地址 `MONGO_HOST = localhost`, 在项目中的任何地方, 除了直接导入`from mySpider.settings import MONGO_HOST` 之外, 还可以使用爬虫(爬虫类如: itcast.py中的ItcastSpider类)中settings属性访问settings文件中的所有配置项: `self.settings["MONGO_HOST"]` 或者 `self.settings.get("MONGO_HOST","")`. 在pipline中的`process_item(self, item, spider)`方法的`spider`参数其实就是爬虫传数据过来的时候把爬虫的实例一并传过来了, 所以用法是`spider.settings.get("MONGO_HOST")`

## pipline的使用

- `open_spider(self, spider)` 方法在爬虫开启的时候执行, 只执行一次, 用于做一些初始化的工作, 貌似在pipline中执行完此方法再去爬虫(爬虫类)中处理引擎传过来的数据, 也可以在此方法中对爬虫对象额外添加一些属性(spider.xxx=xxx), 当我们想把爬虫保存到本地的时候, 也可以在此方法中打开文件, 然后在close_spider()中关闭文件即可
- `close_spider(self, spider)` 此方法在爬虫关闭的时候执行, 仅执行一次

```python
from pymongo import MongoClient

class YangguangPipline(object):
    def open_spider(self, spider):
        # self.file = open(spider.settings.get("SAVE_FILE", "./temp.json"), "w")
        client = MongoClient()
        self.collection = client["test"]["test"]

    def close_spider(self, spider):
        # self.file.close()
```

## CrawlSpider

1. 创建爬虫的时候: `scrapy genspider -t crawl cf "circ.gov.cn"`
2. 进入刚刚创建的爬虫文件`cf.py`中

    ```python
    class CfSpider(CrawlSpider):
        name = 'cf'
        allowed_domains = ['circ.gov.cn']
        start_urls = ['http://www.circ.gov.cn/web/site0/tab5240/module14430/page1.htm']

        # 定义提取url地址规则
        rules = (
            # LinkExtractor 链接提取器, 根据allow的值(正则)提取URL地址(比如下一页的url地址), 到父类的parse()函数发送请求, 所以当前类没有parse()函数, 如果定义了一个parse函数, 将会覆盖掉父类中发送请求的parse()方法
            # callback 提取出来的URL地址在父类parse()方法中请求后得到的响应交由callback处理
            # follow 当前URL地址的响应是否能够重新经过rules来提取地址(详情页中不需要再提取详情页地址了)
            # 提取详情页的URL地址
            Rule(LinkExtractor(allow=r'/web/site0/tab5240/info/\d.+\.htm'), callback='parse_item'),
            # 提取下一页URL地址
            Rule(LinkExtractor(allow=r'/web/site0/tab5240/module14430/page\d+\.htm') follow=True),
        )

        # parse()函数有特殊功能不能定义

        # 详情页的response会交给parse_item处理(rules中指定的)
        def parse_item(self, response):
            item = {}
            # 在详情页中, 通过正则提取标题
            item["title"] = re.findall("<!--TitleStart-->(.*?)<!--TitleEnd-->", response.body.decode())[0]
            # 正则提取发布时间
            item["publish_date"] = re.findall("发布时间: (20\d{2}-\d{2}-\d{2})", response.body.decode())[0]
            # 接下来也是可以yield一个scrapy.Request对象构造一个新的请求...
    ```

3. 补充

- LinkExtractor 更多常见参数
  - deny: 满足正则的URL地址 不被提取
  - allow_domains: 会被提取的链接的domains
  - denydomains: 不会被提取的链接的domains
  - restrict_xpaths: 使用xpath表达式, 和allow共同作用于过滤链接

- spider.Rule 常见参数
  - process_links: 指定该spider中, 哪个的函数将会被调用, 从link_extractor中获取到链接列表时会调用该函数, **该方法主要用来过滤URL**
  - process_request: 指定该spider中哪个函数将会被调用, 该规则提取到每个request时都会调用该函数, **用来过滤request**

## scrapy模拟登录

### 携带cookie登录

- 我们定义的爬虫中有一个属性start_urls, 里面的url是在哪执行的? 在爬虫的父类(scrapy.Spider)中有一个start_request()方法, 此方法会遍历start_urls, 然后yield一个Request()对象出去给scrapy引擎, 和我们自己构建一个请求的过程一样. 所以我们可以在自己创建的爬虫中定义一个start_request()方法, 在完成对start_urls中url构建请求的基础上, 也可以使用cookie模拟登陆
- 代码(携带人人网的cookies访问人人网)

    ```python
    # 新建爬虫renren.py
    class RenrenSpider(scrapy.Spider):
        name = 'renren'
        allowed_domains = ['renren.com']
        start_urls = ['http://www.renren.com/327550029/profile']

        def start_request(self):
            cookies = 'UOR=zz.253.com,widget.weibo.com,www.baidu.com; SUB=_2AkMq-eLCf8NxqwJRmP4XzG3laYR2zA7EieKcpRMZJRMxHRl-yT83ql0ztRB6AXnMLTGE8XdRVtflB16mzIZrdI7Hq-jP; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WF2xGB9bugm1NAM42HdNY.b; SINAGLOBAL=2291322632949.612.1575512805211; ULV=1584342515868:2:1:1:4689987464875.497.1584342515865:1575512805367; login_sid_t=f36504416bb134e43d9d8495e54d9340; cross_origin_proto=SSL; Ugrow-G0=589da022062e21d675f389ce54f2eae7; _s_tentry=www.baidu.com; YF-V5-G0=260e732907e3bd813efaef67866e5183; wb_view_log=1920*10801; Apache=4689987464875.497.1584342515865; WBStorage=42212210b087ca50|undefined'
            # 字典推导式 | 切割字符串
            cookies = {i.split("=")[0]:i.split("=")[1] for i in cookies.split("; ")}
            # 在后续的处理过程中, 如果继续发送一个请求, 会自动携带上cookies(settings中配置COOKIES_DEBUG = True), 后面的请求就不需要带上cookies参数了
            yield scrapy.Request(
                self.start_urls[0],
                callback=self.parse,
                cookies=cookies
            )
    ```

### 发送post请求登录

- 创建一个用于GitHub登录的爬虫 `scrapy genspider github github.com`, 在 `github.py` 中实现爬虫

    ```python
    # github.py
    import re
    class GithubSpider(scrapy.Spider):
        name = 'github'
        allow_domains = ['github.com']
        start_urls = ['http://github.com/login']
        def parse(self, response):
            authenticity_token = response.xpath("//input[@name='authenticity_token']/@value").extract_first()
            utf8 = response.xpath("//input[@name='utf8']/@value").extract_first()
            commit = response.xpath("//input[@name='commit']/@value").extract_first()
            post_data = dict(
                login="sosososolong",
                password="123",
                commit=commit,
                authenticity_token=authenticity_token,
                utf8=utf8
            )
            yield scrapy.FormRequest(
                "https://github.com/session",
                formdata=post_data,
                callback=self.after_login,
            )
        def after_login(self, response):
            print(re.findall("sosososolong|Sosososolong", response.body.decode()))
    ```

### scrapy模拟登录-自动登录

```python
# github2.py
import re
class Github2Spider(scrapy.Spider):
    name='github2'
    allowed_domains=['github.com']
    start_urls=['https://github.com/login']
    def parse(self, response):
        # form_response的意思就是从响应中找到form表单进行登录
        yield scrapy.FormRequest.form_response(
            response, # 自动地从response中寻找表单
            formdata={"login":"sosososolong", "password":"123456"},
            callback=self.after_login
        )
    def after_login(self, response):
        print(re.findall("sosososolong|Sosososolong", response.body.decode()))
```

## 中间件的学习

1. `settings.py`中开启`SPIDER_MIDDLEWARES`配置项(默认注释)即可开启中间件
2. 在`middlewares.py`中添加一个middleware, **并注册到刚刚开启的配置项`SPIDER_MIDDLEWARES`中**

    ```python
    import random
    class RandomUserAgentMiddleware:
        def process_request(self, request, spider):
            # 在settings文件中定义了USER_AGENT_LIST列表,存储了很多的user-agent, 每次请求随机带上一个
            ua = random.choice(spider.settings.get("USER_AGENT_LIST"))
            request.headers["User-Agent"] = ua

    class CheckUserAgent:
        def process_response(self, request, response, spider):
            print(dir(response.request)) # 用dir()方法查看response.request的一些属性和方法, 没有headers属性
            print(request.headers["User-Agent"])
            return response
    ```

## scrapy_redis

- scrapy_redis在scrapy的基础上实现了更多, 更强大的功能, 具体体现在: request去重, 爬虫持久化, 轻松实现分布式

### 开始

- 进入python虚拟环境, 安装scrapy_redis模块 `pip install scrapy_redis`
- 进入GitHub下载搜索并下载scrapy_redis源码 `git clone https://github.com/rmax/scrapy-redis.git`, 其中有一个example-project就是一个demo程序
- 将example-project单独复制出来 `cp -rf scrapy-redis/example-project/ ./`, 打开`settings.py`配置文件, 在最下面配置redis服务器地址 `REDIS_URL = "redis:127.0.0.1:6379"`, 下面是scrapy_redis的一些特殊配置(带"\*"号的), 普通的scrapy项目中添加带"\*"号的四个配置即可将项目转为scrapy_redis项目

    ```python
    # ...
    DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter" # 指定哪个去重方法给Request对象去重 **********
    SCHEDULER = "scrapy_redis.scheduler.Scheduler" # 指定schedule队列 ***************
    SCHEDULER_PERSIST = True # 队列中的内容是否持久保存, 为False的时候还在关闭redis的时候清空redis ********

    ITEM_PIPELINES = {
        'example.pipelines.ExamplePipeline': 300,
        'scrapy_redis.pipelines.RedisPipeline': 400, # scrapy_redis实现items保存到redis
    }

    # ...
    REDIS_URL = "redis:127.0.0.1:6379" # 配置redis地址 *****************
    ```

- 终端启动demo中的爬虫dmoz`scrapy crawl dmoz`, 爬取到几条数据之后停止
- 进入redis, 使用命令`keys *` 查看数据库, 发现多了三个键

    ```shell
    127.0.0.1:6379> keys *
    1) "dmoz:requests"  # Scheduler队列, 获取的过程是pop操作, 即获取一个会去除一个, 待爬取的Request对象(序列化成字符串), 是zset类型, zrange dmoz:requests 0 -1 查看
    2) "dmoz:items"  # list类型, 这里的数据是在RedisPipline中保存的 获取到的item信息
    3) "dmoz:dupefilter"  # set类型, 存储的是抓到过(可能爬过可能还没)的Request对象的指纹
    ```

- 我们已经知道RedisPipline将item数据存储到了reids中, 我们可以新建一个pipline(或者修改默认的pipline)将数据存储到任何一个地方

### Request对象什么时候入队

- dont_filter = True,构造请求的时候,把dont_filter置为True,该url会被反复抓取(同一个url地址的内容会更新的情况, 如贴吧)
- 一个全新的url地址被抓到的时候, 构造request请求
- url地址在start_urls中的时候,会入队,不管之前是否请求过

### scrapy_redis去重方法

- 使用sha1加密request得到指纹
- 把指纹存在redis集合中
- 下一次新来一个request,同样的方式生成指纹,判断指纹是否存在redis集合中
- 生成指纹的代码

    ```python
    fp = hashlib.sha1()
    fp.update(to_bytes(request.method)) # 请求方法
    fp.update(to_bytes(canonicalize_url(request.url))) # 请求地址
    fp.update(request.body or b'') # 请求体
    return fp.hexdigest()
    ```

### 判断数据是否存在redis集合中, 执行插入操作即可

```python
added = self.server.sadd(self.key, fp)
return dded == 0 # True表示没有插入成功, 说明指纹已经存在
```

### 当当爬虫(分布式爬虫)

- 创建爬虫`scrapy genspider dangdang dangdang.com`
- 编辑爬虫文件`dangdang.py`

    ```python
    import scrapy
    from scrapy_redis.spiders import RedisSpider # 将默认爬虫父类scrapy.Spider修改为此类
    from copy import deepcopy
    import urllib

    class DangdangSpider(RedisSpider):
        name='dangdang'
        allowed_domains = ['dangdang.com']
        # start_urls = ['http://book.dangdang.com'] # 可以去掉此配置, 改为如下配置让程序从redis中取(分布式)
        redis_key = "dangdang" # 从redis的"dangdang"这个键取出的值作为allowed_domains的值, pop操作, 分布式的时候,一台服务器抓取了一个地址就把这个地址从数据库中删掉, 这个地址就不会被其他的服务器抓取了

        def parse(self, response):
            # 大分类分组
            div_list = response.xpath("//div[@class='con flq_body']/div")
            for div in div_list:
                item = {}
                item["b_cate"] = div.xpath("./dl/dt//text()").extract() # "//text()"取出的文本将包括换行符和空格
                item["b_cate"] = [i.strip() for i in item["b_cate"] if len(i.trip()) > 0]
                # 中间分类
                dl_list = div.xpath("./div//dl[@class='inner_dl']")
                for dl in dl_list:
                    item[m_cate] = dl.xpath("./dt//text()").extract()
                    item["m_cate"] = [i.strip() for i in item["m_cate"] if len(i.trip()) > 0][0]
                    # 小分类分组
                    a_list = dl.xpath("./dd/a")
                    for a in a_list:
                        item["s_href"] = a.xpath("./@href").extract_first()
                        item["s_cate"] = a.xpath("./text()").extract_first()
                        if item["s_href"] is not None:
                            yield scrapy.Request(
                                item["s_href"],
                                callback=self.parse_book_list,
                                meta={"item":deepcopy(item)}
                            )
        def parse_book_list(self, response):
            item = response.meta["item"]
            li_list = response.xpath("//ul[@class='bigimg']/li")
            for li in li_list:
                item["book_img"] = li.xpath("./div[@class='pic']/img/@src").extract_first()
                if item["book_img"] == "images/model/guan/url_none.png":
                    item["book_img"] = li.xpath("./div[@class='pic']/img/@data-original").extract_first()
                item["book_name"] = li.xpath("./p[@class='name']/a/@title").extract_first()
                item["book_desc"] = li.xpath("./p[@class='detail']/text()").extract_first()
                item["book_price"] = li.xpath(".//span[@class='search_now_price']/text()").extract_first()
                item["book_author"] = li.xpath("./p[@class='search_book_author']/span[1]/a/text()").extract() # 多个作者
                item["book_publish_date"] = li.xpath("./p[@class='search_book_author']/span[2]/text()").extract_first()
                item["book_press"] = li.xpath("./p[@class='search_book_author']/span[3]/a/text()").extract_first()
                print(item)
            # 下一页
            next_url = response.xpath("//li[@class='next']/a/@href").extract_first()
            if next_url is not None:
                urllib.parse.urljoin(response.url, next_url)
                yield scrapy Request(
                    next_url,
                    callback=self.parse_book_list,
                    meta={"item": item}
                )
    ```

### 亚马逊爬虫(scrapy_redis中实现CrawlSpider分布式版本)

- 创建一个新的爬虫`scrapy genspider -t crawl amazon amazon.cn`
- 编辑刚刚创建的爬虫文件`amazon.py`

    ```python
    import scrapy
    from scrapy.linkextractors import LinkExtractor
    from scrapy.spiders import CrawlSpider, Rule
    from scrapy_redis.spiders import RedisCrawlSpider # 将爬虫的默认父类替换成这个

    class AmazonSpider(RedisCrawlSpider):
        name = 'amazon'
        allowed_domains=['amazon.cn']
        # 要实现分布式, 跟当当爬虫一样, 起始地址在redis中设置, 一个地址不同服务器只会爬取一次
        # start_urls = ['https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&url=search-alias%3Dstripbooks&field-keywords=']
        redis_key = "amazon"

        rules = (
            # Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
            # 使用正则的方式匹配获取一级分类和二级分类的url地址(少儿, 文学, 小说, 传记)
            Rule(LinkExtractor(restrict_xpaths=("//div[@class='categoryRefinementsSection']/ul/li",)), follow=True),
            # 匹配图书的url地址
            Rule(LinkExtractor(restrict_xpaths=("//div[@id='mainResults']/ul/li//h2/..",)), callback="parse_book_detail")
            # 列表页翻页
            Rule(LinkExtractor(restrict_xpaths=("//div[@id='pagn']",)), flollow=True)
        )

        def parse_book_detail(self, response):
            item = {}
            item["book_title"] = response.xpath("//span[@id='productTitle']/text()").extract_first()
            item["book_publish_date"] = response.xpath("//h1[@id='title']/span[last()]/text()").extract_first()
            item["book_author"] = response.xpath("//div[@class='byline']/span/a/text()").extract() # 可能多个作者
            item["book_img"] = response.xpath("//div[@id='img-canvas']/img/@src").extract_first()
            item["book_price"] = response.xpath("//div[@id='soldByThirdParty']/span[2]/text()").extract_first()
            item["book_cate"] = response.xpath("//div[@id='wayfinding-breadcrumbs_feature_div']/ul/li[not(@class)]/span/a/text()").extract()
            item["book_press"] = response.xpath("//b[text()='出版社:']/../text()").extract_first()
            item["book_desc"] = re.findall(r'<noscript>.*?<div>(.*?)</div>.*?</noscript>', response.body.decode(), res.S)
            print(item)
    ```

## crontab定时执行爬虫

- 把爬虫执行命令写入.sh爬虫, 比如写一个`spider.sh`

    ```shell
    #!/bin/sh       #表示使用/bin/sh来执行下面的内容
    cd `dirname $0` || exit 1    # cd到当前目录, 失败则退出
    /usr/bin/python ./main.py >> run.log 2>&1    # 把屏幕输出的内容重定向到run.log, 2>&1的作用是把错误也重定向到run.log中
    ```

- 给.sh脚本添加可执行权限 `chmod +x myspider.sh`
- 把.sh程序写入crontab配置文件中`0 6 * * * /home/xxxx/myspider.sh >> /home/xxxx/run2.log 2>&1`, 这里重定向到run2.log中的内容是sh脚本执行的一些输出, 上面是python程序执行过程中屏幕中的输出

## 常用方法

- 正则查看js中的某个数值 `page_count = int(re.findall("var pagecount=(.*?);", response.body.decode())[0])`
- xpath过滤包含的css类的元素 `div_list = response.xpath("//div[contains(@class, 'i')]")`
- xpath根据元素文本过滤 `next_url= response.xpath("//a[text()='下一页']/@href").extract_first()`
- xpath筛选最后一个span标签的文本 `item["book_publish_date"] = response.xpath("//h1[@id='title']/span[last()]/text()").extract_first()`
- 将a标签中href(不完整的url)补全 `urllib.parse.urljoin(response.url, item["href"])`
- 请求得到utf8编码结果: `\u8fd9\u662f\u6768\u9896\uff1f\u6211\u662f\u4e0d\u662f\u9519\u8fc7\u4e86\u4ec0\u4e48` **字符串**,可以使用`bytes(str, 'utf-8')` 将其转换为二进制数据, 再调用decode()方法即可
