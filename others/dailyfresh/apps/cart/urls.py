from cart.views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView
from django.urls import re_path

urlpatterns = [
    re_path(r'^add$', CartAddView.as_view(), name='add'),
    re_path(r'^$', CartInfoView.as_view(), name='show'),  # 购物车页面显示
    re_path(r'^update$', CartUpdateView.as_view(), name='update'),  # 购物车记录更新
    re_path(r'^delete', CartDeleteView.as_view(), name='delete'),  # 购物车删除记录
]