from django.urls import re_path
from . import views
from .views import RegisterView, ActivateView, LoginView


urlpatterns = [
    # re_path(r'^register/', views.register, name='register'),

    re_path(r'^register/$', RegisterView.as_view(), name='register'),
    re_path(r'^active/(?P<token>.*)$', ActivateView.as_view(), name='active'),
    re_path(r'^login[/]{0,1}$', LoginView.as_view(), name='login'),
]
