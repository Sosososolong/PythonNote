from order.views import OrderPlaceView, OrderCommitView, OrderPayView, OrderCheckView, CommentView
from django.urls import re_path

urlpatterns = [
    re_path(r'^place$', OrderPlaceView.as_view(), name='place'),  # 提交订单页面显示
    re_path(r'^commit$', OrderCommitView.as_view(), name='commit'),  # 提交创建
    re_path(r'^pay$', OrderPayView.as_view(), name='pay'),  # 订单支付
    re_path(r'^check$', OrderCheckView.as_view(), name='check'),  # 订单查询
    re_path(r'^comment/(?P<order_id>.+)$', CommentView.as_view(), name='comment'),  # 评论
]
