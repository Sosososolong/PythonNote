from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext
from celery import Celery
import time
# 在任务处理者加这几句
import os
# import django
# 下面两行是任务处理者启动django的语句, 在任务处理者中, 如果要导入django的模型等模块, 需要在启动django后导入
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()
# 在这里, 下面的导入模块可以移到上面也可以, 但是在任务处理者中如果要导入django中的模块, 需要在启动django后
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://192.168.1.111:6379/8')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎成为天天生鲜注册会员</h1>请点击下面的链接激活您的账号<br/> <a href="http://127.0.0.1:8000/user/active/%s">请点击此处激活账户</a>' % (
        username, token)
    print(html_message)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)


@app.task
def generate_static_index_html():
    """生成首页静态页面"""
    """显示首页"""
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    data = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 1.加载模板文件, 返回 模板对象
    template = loader.get_template('static_index.html')
    # 2.定义模板上下文, 给模板文件传递数据(上下文中没有request对象,所以就省略此行代码,也是可以顺利执行的)
    # context = RequestContext(request, data)
    # 3.模板渲染, 返回 标准的html内容(字符串)
    static_index_html = template.render(data)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')

    with open(save_path, 'w') as f:
        f.write(static_index_html)
