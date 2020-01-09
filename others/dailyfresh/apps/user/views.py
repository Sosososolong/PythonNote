from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings

from django.views.generic.base import View
from celery_tasks.tasks import send_register_active_email
from utils.mixin import LoginRequiredMixin

from django_redis import get_redis_connection

from .models import User, Address


# Create your views here.
def index(request):
    return render(request, 'user/index.html')


def register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    else:
        '''进行注册处理'''
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)

        # 返回应答, 跳转到首页
        return redirect(reverse('goods:index'))


class RegisterView(View):
    """注册"""
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        """进行注册处理"""
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'user/register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'user/register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            # 用户名存在
            return render(request, 'user/register.html', {'errmsg': '用户名已经存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送邮件激活账号，包含激活链接，需要包含用户身份信息，并且加密
        # print(settings.SECRET_KEY)
        serializer = Serializer(settings.SECRET_KEY, 300)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # 加密
        token = token.decode()  # utf-8解码

        # 经过装饰的任务函数可以用以下方式 发送任务
        send_register_active_email.delay(email, username, token)

        # 返回应答, 跳转到首页
        return redirect(reverse('goods:index'))


class ActivateView(View):
    """用户激活"""
    def get(self, request, token):
        """进行用户激活"""
        # 解密用户信息
        serializer = Serializer(settings.SECRET_KEY, 300)
        try:
            info = serializer.loads(token)
            # 获取用户id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(pk=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录视图
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接已经过期')


class LoginView(View):
    """登录"""
    def get(self, request):
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 使用模板
        return render(request, 'user/login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'user/login.html', {'errmsg': '数据不完整'})

        # 业务处理: 登录校验, 使用系统的认证
        user = authenticate(username=username, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                # 记录用户的登录状态(session缓存用户信息, 配置了django-redis, 用户信息将被存储于redis中)
                login(request, user)

                # 获取登录后所要跳转的地址, 默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转 next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'user/login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或者密码错误
            return render(request, 'user/login.html', {'errmsg': '用户名或者密码错误'})

        # 返回应答


# /user/logout
class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """退出登录"""
        # 清除用户的session
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心信息页面"""
    def get(self, request):
        """显示"""
        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # 连接redis方法一
        # from redis import StrictRedis
        # StrictRedis(host='192.168.1.111', port=6379, db=9)
        # 连接redis方法二, 'default'相当于从settings.py中拿到redis配置中的default属性的值, 里面又连接字符串等信息
        con = get_redis_connection('default')  # from django_redis import get_redis_connection
        # 每个用户的历史浏览记录在redis中的存储格式  history_user_id: [2,3,1], 每次都向集合左边添加数据
        history_key = 'history_%d' % user.id
        # 获取用户最新浏览的5个商品id
        sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]
        # 从数据库中查询用户浏览的商品的具体信息
        from goods.models import GoodsSKU
        goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        goods_res = []
        # 按时间倒序顺序排序数据
        for sorted_id in sku_ids:
            for goods in goods_li:
                if sorted_id == goods.id:
                    goods_res.append(goods)

        # 组织上下文
        context = {
            'page': 'user',
            'address': address,
            'goodsli': goods_res
        }

        # django会给request对象添加一个user属性, 如果用户未登录, user是AnonymousUser类的一个实例, 如果用户登录了, user是User类的一个实例
        # request.user.is_authenticated 属性值判断用户是否登录过
        # 除了你给模板文件传递的模板变量之外, django框架会把request.user也传递给模板文件
        return render(request, 'user/user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户订单信息页面"""
    def get(self, request):
        """显示"""
        # 获取订单信息
        return render(request, 'user/user_center_order.html', {'page': 'order'})


# /user/address
class AddressView(LoginRequiredMixin, View):
    """用户地址页面"""
    def get(self, request):
        """显示"""
        # 登录用户
        user = request.user
        # 获取用户的默认收货地址
        address = Address.objects.get_default_address(user)

        return render(request, 'user/user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        """添加地址"""
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user/user_center_site.html', {'errmsg': '数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}', phone):
            return render(request, 'user/user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理: 添加地址
        # 如果用户已存在默认地址, 添加的地址不作为默认收货地址, 否则作为默认收货地址
        # 获取登录用户对应的User对象
        user = request.user
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回应答, 刷新地址页面
        return redirect(reverse('user:address'))  # get请求
