from django.urls import re_path
from goods.views import IndexView, DetailView, ListView

urlpatterns = [
    re_path(r'^index$', IndexView.as_view(), name='index'),  # 首页
    re_path(r'^detail/(?P<goods_id>\d+)$', DetailView.as_view(), name='detail'),  # 首页
    re_path(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list')
]
