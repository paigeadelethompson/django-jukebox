"""
Views for Music Player interface.
"""
from django.conf import settings
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.forms import ModelForm
from django.db.models import Q
from django.urls import reverse
from django_jukebox.music_db.models import Song, SongRating, SONG_RATINGS
from django_jukebox.music_player.models import SongRequest
from django_jukebox.includes.json import JSMessage
from django.views.decorators.csrf import csrf_exempt


class SongUploadForm(ModelForm):
    """
    File Upload form.
    """
    class Meta:
        model = Song
        fields = ('file',)


def music_player_main(request):
    """
    Main view for the music player.
    """
    pagevars = {
        "page_title": settings.PROGRAM_NAME,
        "song_upload_form": SongUploadForm(),
    }

    return render(request, 'index.html', pagevars)


def process_song_upload(request):
    """
    Processes the form data from the upload section of the index
    page.
    """
    if request.POST:
        form = SongUploadForm(request.POST, request.FILES)
    else:
        return HttpResponse("No data")

    if form.is_valid():
        form.save()
        return redirect('music_player_main')
        # return HttpResponseRedirect(reverse('music_player-edit_song',
        # args=[form.instance.id]))
    else:
        return HttpResponse("Invalid data")


class SongRatingForm(ModelForm):
    """
    This form is used in the Currently Playing bar at the top. It is only
    really used for rendering, not validation.
    """
    class Meta:
        model = SongRating
        fields = ('rating',)

    def __init__(self, *args, **kwargs):
        super(SongRatingForm, self).__init__(*args, **kwargs)

        # In very rare instances, we might not have a current song playing.
        # Rather than throw server errors, just send a -1, which the
        # Javascript understands means no song.
        if self.instance:
            song_id = self.instance.song.id
        else:
            song_id = -1

        # Set the JavaScript event handler for sending ratings.
        self.fields["rating"].widget.attrs = {
            'onchange': 'javascript:rating_change_handler(%s)' % song_id
        }


def display_currently_playing(request):
    """
    The logic for the "CURRENTLY PLAYING" header at the top. Also renders the
    drop-down for rating songs.
    """
    try:
        currently_playing_track = SongRequest.objects.filter(time_played__isnull=False).order_by('-time_played')[0]
    except IndexError:
        currently_playing_track = None

    pagevars = {
        "currently_playing_track": currently_playing_track,
    }

    if currently_playing_track and request.user.is_authenticated():
        # Only allow logged in users to rate songs.
        rating, created = SongRating.objects.get_or_create(
            song=currently_playing_track.song,
            user=request.user)
        # Make this a bound form.
        form = SongRatingForm(instance=rating)
    else:
        form = None

    pagevars["rating_form"] = form

    return render(request, 'currently_playing.html', pagevars)

# FIXME: Make the UI use CSRF properly.


@csrf_exempt
def rate_song(request):  # , song_id, rating):
    """
    Rates a song.
    """
    song_id = int(request.POST['song_id'])
    rating = int(request.POST['rating_value'])

    song = get_object_or_404(Song, id=song_id)

    request_user = request.user
    if not request.user.is_authenticated():
        # Can't store AnonymousUser objects in a ForeignKey to User.
        # Only allow auth'd users to rate.
        return HttpResponse(JSMessage("User not authenticated.",
                                      is_error=True))
    else:
        rating_obj, created = SongRating.objects.get_or_create(song=song,
                                                               user=request.user)
        if rating < 0:
            # A rating of 0 means no rating. Let them un-rate songs they
            # have rated, like iTunes.
            rating = None

        if rating > 4:
            rating = 4

        rating_obj.rating = rating
        rating_obj.save()
        return HttpResponse(JSMessage("Rating sent."))


def display_song_queue(request):
    """
    Display the song queue. Previously played, currently playing, upcoming
    user requests, then upcoming random requests.
    """
    try:
        currently_playing_track = SongRequest.objects.filter(time_played__isnull=False).order_by('-time_played')[0]
        recently_played_tracks = SongRequest.objects.filter(time_played__isnull=False).exclude(
            id=currently_playing_track.id).order_by('-time_played')[:settings.NUMBER_OF_PREVIOUS_SONGS_DISPLAY]
    except IndexError:
        currently_playing_track = None
        recently_played_tracks = SongRequest.objects.filter(time_played__isnull=False).order_by(
            '-time_played')[:settings.NUMBER_OF_PREVIOUS_SONGS_DISPLAY]

    """
	Determine total number of songs being displayed. Display as many songs as
	have been requested by users, but if that number is less than the
	LIMIT_UPCOMING_SONGS_DISPLAY setting, fill out with randomly generated requests
	until that number is reached.
	"""
    total_displayed_songs = settings.LIMIT_UPCOMING_SONGS_DISPLAY
    upcoming_requested_tracks = SongRequest.objects.get_pending_user_requests()
    if upcoming_requested_tracks.count() < total_displayed_songs:
        random_song_display_limit = total_displayed_songs - upcoming_requested_tracks.count()
        upcoming_random_tracks = SongRequest.objects.get_pending_anonymous_requests()[:random_song_display_limit]
    else:
        upcoming_random_tracks = None

    pagevars = {
        "page_title": "Song Queue",
        "recently_played_tracks": recently_played_tracks,
        "currently_playing_track": currently_playing_track,
        "upcoming_requested_tracks": upcoming_requested_tracks,
        "upcoming_random_tracks": upcoming_random_tracks,
    }

    return render(request, 'song_list.html', pagevars)


class SongSearchForm(forms.Form):
    """
    Search form model. Only one field that will search across multiple columns.
    """
    keyword = forms.CharField()


@csrf_exempt
def song_search(request):
    """
    Search form for songs. Find songs, request them... pretty basic.
    """
    total_songs = Song.objects.all().count()
    pagevars = {
        "page_title": "Song Search",
        "form": SongSearchForm(),
        "total_songs": total_songs,
    }

    return render(request, 'song_search.html', pagevars)


def song_upload(request):
    """
    Upload form for songs.
    """
    pagevars = {
        "page_title": "Song Upload",
        "form": SongUploadForm(),
    }

    return render(request, 'song_upload.html', pagevars)


@csrf_exempt
def song_search_results(request, qset=Song.objects.all()):
    """
    Query Song model based on search input.
    """
    form = SongSearchForm(request.POST)

    if request.POST and form.is_valid():
        s_search = form.cleaned_data.get("keyword", None)
        if s_search:
            qset = qset.filter(Q(artist__icontains=s_search) |
                               Q(title__icontains=s_search) |
                               Q(album__icontains=s_search) |
                               Q(genre__icontains=s_search)).order_by('artist',
                                                                      'title')
    else:
        qset = qset.order_by('?')[:10]

    pagevars = {
        "qset": qset,
    }

    return render(request, 'song_results.html', pagevars)

# FIXME: Make the UI use CSRF properly.


@csrf_exempt
def request_song(request):  # , song_id):
    """
    Create a new SongRequest object for the given song id.
    """
    request_user = request.user
    song_id = long(request.POST['song_id'])
    if not request.user.is_authenticated():
        # Set this to None to avoid storing an AnonymousUser in the
        # SongRequest (this would raise an exception).
        request_user = None
        # You can allow anonymous user requests in settings.py.
        if not settings.ALLOW_ANON_REQUESTS:
            # Anonymous user requests not allowed, error out.
            message = JSMessage("You must be logged in to request songs.",
                                is_error=True)
            return HttpResponse(message)

    # Look the song up and create a request.
    song = Song.objects.get(id=song_id)
    if SongRequest.objects.get_active_requests().filter(song=song):
        # Don't allow requesting a song that is currently in the queue.
        return HttpResponse(JSMessage("Song has already been requested.",
                                      is_error=True))
    elif SongRequest.objects.get_active_requests().filter(requester=request_user).count() >= settings.MAX_OUTSTANDING_REQUESTS_PER_USER:
        return HttpResponse(JSMessage("You've already got the maximum number of outstanding requests.", is_error=True))
    else:
        # Song isn't already in the SongRequest queue, add it.
        request = SongRequest(song=song, requester=request_user)
        request.save()
        return HttpResponse(JSMessage("Song Requested."))


@csrf_exempt
def skip_song(request):
    if request.method != 'POST':
        return HttpResponse(JSMessage("Invalid method."))

    if not request.user.is_authenticated():
        return HttpResponse(JSMessage("Unauthenticated users aren't allowed to do this."))

    if not request.user.has_perm('music_player.can_skip_song'):
        return HttpResponse(JSMessage("You don't have permission to do that."))

    # TODO: Make this better by implementing the music_daemon better such that we can control
    # playback of music programatically.
