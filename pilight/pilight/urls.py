from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from home import views

admin.autodiscover()

# Home
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^driver/start/?$', views.start_driver, name='start_driver'),
    url(r'^driver/stop/?$', views.stop_driver, name='stop_driver'),
    url(r'^driver/restart/?$', views.restart_driver, name='restart_driver'),
    url(r'^light/render_snippet/?$', views.render_lights_snippet, name='render_lights_snippet'),
    url(r'^light/apply_tool/?$', views.apply_light_tool, name='apply_light_tool'),
    url(r'^light/simulate/?$', views.run_simulation, name='run_simulation'),
    url(r'^light/fill_color/?$', views.fill_color, name='fill_color'),
    url(r'^transform/render_snippet/?$', views.render_transforms_snippet, name='render_transforms_snippet'),
    url(r'^transform/add/?$', views.add_transform, name='add_transform'),
    url(r'^transform/delete/?$', views.delete_transform, name='delete_transform'),
    url(r'^transform/updateparams/?$', views.update_transform_params, name='update_transform_params'),
    url(r'^store/load/?$', views.load_store, name='load_store'),
    url(r'^store/render_snippet/?$', views.render_stores_snippet, name='render_stores_snippet'),
    url(r'^store/save/?$', views.save_store, name='save_store'),
    url(r'^channel/set/?$', views.update_color_channel, name='update_color_channel'),
    url(r'^auth/?$', views.post_auth, name='post_auth'),
]

# Auth
urlpatterns += [
    url(r'^accounts/login/?$', auth_views.login),
    url(r'^accounts/logout/?$', auth_views.logout, {'next_page': '/'}),
]

# Admin
urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
]
