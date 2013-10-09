from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Home
urlpatterns = patterns(
    'home.views',
    url(r'^/?$', 'index', name='index'),
    url(r'^start/?$', 'start', name='start'),
    url(r'^stop/?$', 'stop', name='stop'),
    url(r'^lights/render/?$', 'render_lights_snippet', name='render_lights'),
    url(r'^lights/apply_tool/?$', 'apply_light_tool', name='apply_light_tool'),
)

# Admin
urlpatterns += patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
