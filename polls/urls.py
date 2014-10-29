from django.conf.urls import patterns, url

from polls import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='markets'),
    url(r'^(?P<pk>\d+)/$', views.market_view, name='market'),
    url(r'^(?P<qid>\d+)/join/$', views.market_join, name='market_join'),
)
