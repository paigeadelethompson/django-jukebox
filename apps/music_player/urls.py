from django.conf.urls.defaults import *

urlpatterns = patterns('apps.music_player.views',
	url(r'^$', 'music_player_main', 
		name='music_player_main'),
	url(r'^song_queue/$', 'display_song_queue', 
		name='music_player-display_song_queue_div'),
	url(r'^currently_playing/$', 'display_currently_playing', 
		name='music_player-display_currently_playing_div'),
	url(r'^song_search/$', 'song_search', 
		name='music_player-song_search_div'),
	url(r'^song_upload/$', 'song_upload', 
		name='music_player-song_upload'),
	url(r'^song_upload/process/$', 'process_song_upload',
		name='music_player-process_song_upload'),
	#url(r'^edit_song/(?P<song_id>\d+)/$', 'edit_song', 
	#	name='music_player-edit_song'),
	url(r'^song_search_results/$', 'song_search_results', 
		name='music_player-ajax-song_search_results'),
	url(r'^request_song/$', 'request_song', 
		name='music_player-ajax-request_song'),
	url(r'^rate_song/$', 'rate_song', 
		name='music_player-ajax-rate_song'),
	url(
		r'^skip_song/$',
		'skip_song',
		name='music_player-ajax-skip_song'
	),
)
