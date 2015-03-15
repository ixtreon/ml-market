from django.conf.urls import patterns, url, include

from markets import views
from rest_framework import routers
from markets.viewsets import MarketViewSet



urlpatterns = patterns('',
    url(r'^$', views.MarketIndexView.as_view(), name='markets'),
    url(r'^(?P<pk>\d+)/$', views.market_index, name='market'),
    url(r'^remove_order/(?P<pk>\d+)/$', views.order_remove, name='remove_order'),
    url(r'^(?P<pk>\d+)/join/$', views.market_join, name='market_join'),
    url(r'^(?P<pk>\d+)/hist/', views.market_activity),
    #url(r'^(?P<pk>\d+)/bet/$', views.market_bet, name='market_bet'),
    #url(r'^(?P<pk>\d+)/orders/$', views.market_view_orders, name='market_orders'),
)