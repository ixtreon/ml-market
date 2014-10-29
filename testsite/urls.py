from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
import polls

urlpatterns = patterns('',
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'polls:markets'}, name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^market/', include('polls.urls', namespace='polls')),
    url(r'^upload/', polls.views.upload_file, name='upload'),
    url(r'^user/', polls.views.user_info, name='user'),
)
