from django.conf.urls import include, url
from django.contrib import admin

from home import views

admin.autodiscover()

# Home
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/?$', views.bootstrap_client, name='bootstrap_client'),
    url(r'^api/driver/start/?$', views.start_driver, name='start_driver'),
    url(r'^api/driver/stop/?$', views.stop_driver, name='stop_driver'),
    url(r'^api/driver/restart/?$', views.restart_driver, name='restart_driver'),
    url(r'^api/light/base-colors/?$', views.get_base_colors, name='get_base_colors'),
    url(r'^api/light/apply-tool/?$', views.apply_light_tool, name='apply_light_tool'),
    url(r'^api/light/preview/?$', views.preview, name='preview'),
    url(r'^api/light/fill-color/?$', views.fill_color, name='fill_color'),
    url(r'^api/transform/add/?$', views.add_transform, name='add_transform'),
    url(r'^api/transform/delete/?$', views.delete_transform, name='delete_transform'),
    url(r'^api/transform/update/?$', views.update_transform, name='update_transform'),
    url(r'^api/transform/reorder/?$', views.reorder_transforms, name='reorder_transforms'),
    url(r'^api/variable/add/?$', views.add_variable, name='add_variable'),
    url(r'^api/variable/delete/?$', views.delete_variable, name='delete_variable'),
    url(r'^api/variable/update/?$', views.update_variable, name='update_variable'),
    url(r'^api/config/load/?$', views.load_config, name='load_config'),
    url(r'^api/config/save/?$', views.save_config, name='save_config'),
    url(r'^api/channel/set/?$', views.update_color_channel, name='update_color_channel'),
]

# Auth
urlpatterns += [
    url(r'^api/auth/login/?$', views.login, name='login'),
    url(r'^api/auth/logout/?$', views.logout, name='logout'),
]

# Admin
urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
]
