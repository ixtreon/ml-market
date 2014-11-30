from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import markets.views
from django.views.generic.base import TemplateView
from rest_framework import routers
from markets.viewsets import MarketViewSet


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'markets', MarketViewSet)

# declares the site-wide URLs to be used
urlpatterns = patterns('',
    # index
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    # admin interface
    url(r'^admin/', include(admin.site.urls)),
    # user actions
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'markets:markets'}, name='logout'),
    url(r'^user/', markets.views.user_info, name='user'),
    url(r'^market/', include('markets.urls', namespace='markets')),
    url(r'^upload/', markets.views.upload_file, name='upload'),
    ## django-rest-framework
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)