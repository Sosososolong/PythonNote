from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings

from django.views.generic.base import View
from celery_tasks.tasks import send_register_active_email

from .models import User


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
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

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

                # 跳转首页
                response = redirect(reverse('goods:index'))  # HttpResponseRedirect

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

