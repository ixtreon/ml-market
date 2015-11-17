from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import markets.views
from django.views.generic.base import TemplateView
from rest_framework import routers
from markets.api.viewsets import *
from markets.api.views import api_bid, api_register, api_cancel_bid


# Routers are used with django-rest-framework to automatically map views to urls
router = routers.DefaultRouter()
router.register(r'play', PlayViewSet, base_name='play')
router.register(r'markets', MarketViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'datasets', DataSetViewSet)
router.register(r'data', DatumViewSet)

# declares the site-wide URLs to be used
urlpatterns = patterns('',
    
    # market admin
    url(r'^admin/', include(admin.site.urls)),
    
    # user admin
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'markets:markets'}, name='logout'),
    url(r'^user/(?P<uid>\w*)', markets.views.user_info, name='user'),
    
    # index page
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    
    # market pages
    url(r'^market/', include('markets.urls', namespace='markets')),
    
    
    ## RESTful API interface
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API actions
    url(r'^api/bid/(?P<mkt>\w*)$', api_bid, name='api_bid'),
    url(r'^api/cancel/(?P<pk>\w*)$', api_cancel_bid, name='api_cancel_bid'),
    url(r'^api/register/(?P<pk>\w*)$', api_register, name='api_register'),
)