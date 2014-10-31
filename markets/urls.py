from django.conf.urls import patterns, url

from markets import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='markets'),
    url(r'^(?P<pk>\d+)/$', views.market_view, name='market'),
    url(r'^remove_order/(?P<pk>\d+)/$', views.order_remove, name='remove_order'),
    url(r'^(?P<qid>\d+)/join/$', views.market_join, name='market_join'),
)
