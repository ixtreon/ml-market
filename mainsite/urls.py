from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import markets

urlpatterns = patterns('',
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'markets:markets'}, name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^market/', include('markets.urls', namespace='markets')),
    url(r'^upload/', markets.views.upload_file, name='upload'),
    url(r'^user/', markets.views.user_info, name='user'),
)
