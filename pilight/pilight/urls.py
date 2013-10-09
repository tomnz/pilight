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
    url(r'^light/render_snippet/?$', 'render_lights_snippet', name='render_lights_snippet'),
    url(r'^light/apply_tool/?$', 'apply_light_tool', name='apply_light_tool'),
    url(r'^transform/render_snippet/?$', 'render_transforms_snippet', name='render_transforms_snippet'),
    url(r'^transform/add/?$', 'add_transform', name='add_transform'),
    url(r'^transform/delete/?$', 'delete_transform', name='delete_transform'),
    url(r'^transform/updateparams/?$', 'update_transform_params', name='update_transform_params'),
)

# Admin
urlpatterns += patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
