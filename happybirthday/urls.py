from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'happybirthday.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^timeline/', include('timeline.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
