from django.urls import re_path
from .views import RegisterView, ActivateView, LoginView, LogoutView, UserInfoView, UserOrderView, AddressView


urlpatterns = [
    # re_path(r'^register/', views.register, name='register'),

    re_path(r'^register/$', RegisterView.as_view(), name='register'),
    re_path(r'^active/(?P<token>.*)$', ActivateView.as_view(), name='active'),
    re_path(r'^login[/]{0,1}$', LoginView.as_view(), name='login'),
    re_path(r'^logout[/]{0,1}$', LogoutView.as_view(), name='logout'),  # 注销登录
    re_path(r'^$', UserInfoView.as_view(), name='user'),  # 用户中心-信息页
    re_path(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name='order'),  # 用户中心-订单页
    re_path(r'^address$', AddressView.as_view(), name='address'),  # 用户中心-订单页
]
