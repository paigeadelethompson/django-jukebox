from django.urls import include, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.static import serve as static_serve

import django_jukebox.accounts.urls
import django_jukebox.juketunes_ui.urls
import django_jukebox.music_player.urls

urlpatterns = [
    re_path(r'jtui/', include(django_jukebox.juketunes_ui.urls)),
    re_path(r'^accounts/', include(django_jukebox.accounts.urls)),
    re_path(r'^', include(django_jukebox.music_player.urls)),
    re_path(r'^admin/', admin.site.urls),
]