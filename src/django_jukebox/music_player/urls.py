from django.urls import path, re_path
from django.contrib import admin

from django_jukebox.music_player.views import music_player_main, display_song_queue, display_currently_playing, song_search, song_upload, process_song_upload, song_search_results, request_song, rate_song, skip_song

urlpatterns = [
	re_path(r'^$', music_player_main, 
		name='music_player_main'),
	re_path(r'^song_queue/$', display_song_queue, 
		name='music_player-display_song_queue_div'),
	re_path(r'^currently_playing/$', display_currently_playing, 
		name='music_player-display_currently_playing_div'),
	re_path(r'^song_search/$', song_search, 
		name='music_player-song_search_div'),
	re_path(r'^song_upload/$', song_upload, 
		name='music_player-song_upload'),
	re_path(r'^song_upload/process/$', process_song_upload,
		name='music_player-process_song_upload'),
	#url(r'^edit_song/(?P<song_id>\d+)/$', 'edit_song', 
	#	name='music_player-edit_song'),
	re_path(r'^song_search_results/$', song_search_results, 
		name='music_player-ajax-song_search_results'),
	re_path(r'^request_song/$', request_song, 
		name='music_player-ajax-request_song'),
	re_path(r'^rate_song/$', rate_song, 
		name='music_player-ajax-rate_song'),
	re_path(
		r'^skip_song/$',
		skip_song,
		name='music_player-ajax-skip_song'
	),
]