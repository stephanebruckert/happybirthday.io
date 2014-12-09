__author__ = 'stephane bruckert'

from django.conf.urls import url

from timeline import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stats/', views.stats, name='stats'),
    url(r'^facebook_javascript_login_sucess/$', views.facebook_javascript_login_sucess),
]
