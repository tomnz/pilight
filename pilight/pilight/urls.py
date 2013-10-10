from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Home
urlpatterns = patterns(
    'home.views',
    url(r'^/?$', 'index', name='index'),
    url(r'^driver/start/?$', 'start_driver', name='start_driver'),
    url(r'^driver/stop/?$', 'stop_driver', name='stop_driver'),
    url(r'^driver/restart/?$', 'restart_driver', name='restart_driver'),
    url(r'^light/render_snippet/?$', 'render_lights_snippet', name='render_lights_snippet'),
    url(r'^light/apply_tool/?$', 'apply_light_tool', name='apply_light_tool'),
    url(r'^light/simulate/?$', 'run_simulation', name='run_simulation'),
    url(r'^transform/render_snippet/?$', 'render_transforms_snippet', name='render_transforms_snippet'),
    url(r'^transform/add/?$', 'add_transform', name='add_transform'),
    url(r'^transform/delete/?$', 'delete_transform', name='delete_transform'),
    url(r'^transform/updateparams/?$', 'update_transform_params', name='update_transform_params'),
    url(r'^store/load/?$', 'load_store', name='load_store'),
    url(r'^store/render_snippet/?$', 'render_stores_snippet', name='render_stores_snippet'),
    url(r'^store/save/?$', 'save_store', name='save_store'),
)

# Admin
urlpatterns += patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
