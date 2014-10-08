from django.conf.urls import patterns, url

from polls import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='markets'),
    url(r'^(?P<qid>\d+)/$', views.claim, name='market'),
    url(r'^(?P<qid>\d+)/bid/$', views.bid, name='market_bid'),
)
