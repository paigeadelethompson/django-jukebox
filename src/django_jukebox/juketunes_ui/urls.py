from django.urls import path, re_path
from django.contrib import admin

from django_jukebox.juketunes_ui.views.main import view_main
from django_jukebox.juketunes_ui.views.ajax import ajax_get_artist_list, ajax_get_album_list, ajax_get_song_list

urlpatterns = [
    re_path(r'^$', view_main, name='juketunes_ui-main'),
    re_path(r'^ajax/get_artist_list/$', ajax_get_artist_list, 
        name='juketunes_ui-ajax_get_artist_list'),
    re_path(r'^ajax/get_album_list/$', ajax_get_album_list, 
        name='juketunes_ui-ajax_get_album_list'),
    re_path(r'^ajax/get_song_list/$', ajax_get_song_list, 
        name='juketunes_ui-ajax_get_song_list'),
]