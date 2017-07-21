from home.models import Config, Light, Playlist, PlaylistConfig, TransformInstance, VariableInstance, VariableParam
from django.contrib import admin

admin.site.register(Config)
admin.site.register(Light)
admin.site.register(Playlist)
admin.site.register(PlaylistConfig)
admin.site.register(TransformInstance)
admin.site.register(VariableInstance)
admin.site.register(VariableParam)
