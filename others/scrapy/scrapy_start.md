# 入门

## 环境

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
