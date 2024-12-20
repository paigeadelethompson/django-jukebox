import os
import sys
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import signals
from django_jukebox.music_db.managers import SongManager


class Song(models.Model):
    """
    This model represents a single song in the library.
    """
    title = models.CharField(max_length=255, default="Unknown")
    artist = models.CharField(max_length=255, default="Unknown")
    album = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    # Song length (seconds)
    length = models.IntegerField(blank=True, null=True)
    # track_number = models.IntegerField(blank=True, null=True)
    # disc_number = models.IntegerField(blank=True, null=True)
    # If this is True, allow this song to be selected by the random
    # playback mechanism (in the absence of any queue entries).
    allow_random_play = models.BooleanField(default=True)
    # Number of times the song has been requested.
    request_count = models.IntegerField(default=0)
    # Average of all ratings for this song.
    rating = models.FloatField(blank=True, null=True)
    # Cache number of ratings for easier querying in playlist generation.
    num_ratings = models.IntegerField(default=0)

    # store the file inside Django's storage system.
    file = models.FileField(
        upload_to=settings.MUSIC_DIR_NAME,
        max_length=255,
        null=True,
        blank=True
    )

    # if this is set, this will override "file" and point to a local path instead.
    local_path = models.CharField(
        max_length=512,
        blank=True,
        null=True
    )

    def get_local_path(self):
        if self.local_path is not None:
            return self.local_path
        else:
            return self.file.path

    # Who added (uploaded) the Song.
    added_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    # When the song was added to the library.
    time_added = models.DateTimeField(auto_now_add=True)
    # The time the song was last played, requested or automatically.
    time_last_played = models.DateTimeField(blank=True, null=True)
    # Time the song was specifically requested to play.
    time_last_requested = models.DateTimeField(blank=True, null=True)

    objects = SongManager()

    class Meta:
        ordering = ['artist', 'album', 'title']

    def __unicode__(self):
        return "%s - %s" % (self.artist, self.title)

    def populate_from_id3_tags(self, file_path, file_name):
        """
        Read ID3 tags of the mp3 file.

        file_path: (str) Path to a file to load ID3 tags from. This is
                                         generally supplied by song_pre_save().
        file_name: (str) When uploading files from a browser, a temporary
                                         file is used through much of the process. This is
                                         passed so that the file name may be used when invalid
                                         or no tags are found, instead of the scrambled file
                                         name that the temporary upload file uses.
        """
        audio = MP3(file_path)
        tag = audio.tags

        # don't worry about catching errors from this, it means it's not an mp3 file.
        # check file length is not greater than max.

        # TODO: Make this more verbose to the user.
        if audio.info.length > settings.MAX_SONG_LENGTH:
            sys.stderr.writelines(["Audio is longer than maximum allowed."])

        if audio.info.length < settings.MIN_SONG_LENGTH:
            sys.stderr.writelines(["Audio is shorter than minimum allowed."])

        try:

            # print tag
            # Map ID3 tags to columns in the Song table.
            # ID3 Reference: http://www.id3.org/id3v2.4.0-frames
            try:
                self.title = str(tag['TIT2'])
            except KeyError:
                # No tag for title found, use file name.
                self.title = file_name

            try:
                self.artist = str(tag['TPE1'])
            except KeyError:
                pass

            try:
                self.album = str(tag['TALB'])
            except KeyError:
                pass

            try:
                self.genre = str(tag['TCON'])
            except KeyError:
                pass

            # Track numbers are stored in ID3 tags as '1/10' (track/total tracks)
            # Split and just store the track number.
            # try:
            # self.track_number = str(tag['TRCK']).split('/')[0]
            # except KeyError:
            # pass
            #
            # Disc sets are treated much the same way.
            # try:
            # self.disc_number = str(tag['TPOS']).split('/')[0]
            # except KeyError:
            # pass

        except mutagen.id3.ID3NoHeaderError:
            # Invalid ID3 headers. Just use the file name as the title.
            self.title = file_name

    def populate_from_mp4_tags(self, file_path, file_name):
        """
        Populate record from m4a/mp4 data.
        """
        a = MP4(file_path)
        tag = a.tags

        # TODO: Make this more verbose to the user.
        if a.info.length > settings.MAX_SONG_LENGTH:
            sys.stderr.writelines(["Audio is longer than maximum allowed."])

        if a.info.length < settings.MIN_SONG_LENGTH:
            sys.stderr.writelines(["Audio is shorter than minimum allowed."])

        try:

            # print tag
            # Map MP4 tags to columns in the Song table.
            try:
                self.title = tag['title'][0]
            except KeyError:
                # No tag for title found, use file name.
                self.title = file_name

            try:
                self.artist = tag['artist'][0]
            except KeyError:
                pass

            try:
                self.album = tag['album'][0]
            except KeyError:
                pass

            try:
                self.genre = tag['genre'][0]
            except KeyError:
                pass

            # TODO: Handle track number and disc number from mp4 tags.

        except BaseException:
            # Invalid headers. Just use the file name as the title.
            self.title = file_name


def song_pre_save(sender, instance, *args, **kwargs):
    """
    Things to happen in the point of saving an song before the actual save()
    call happens.
    """
    # If the Item has a Null or False value for its 'id' field, it's a new
    # item. Give it a new num_in_job.
    if not instance.id:
        if instance.local_path is None:
            # The file name is used when there are no ID3 tags indicating title.
            file_name = os.path.basename(instance.file.file.name)
            if hasattr(instance.file.file, 'temporary_file_path'):
                # This is probably being uploaded from a form. Use TempUploadFile
                # to figure out where the file is -currently- (before being saved).
                file_path = instance.file.file.temporary_file_path()
            else:
                # This song is being added via a script and is already probably
                # in the music directory.
                file_path = instance.file.path
        else:
            file_name = os.path.basename(instance.local_path)
            file_path = instance.local_path

        if file_name.endswith('.mp4') or file_name.endswith('.m4a'):
            # MP4/M4A, analyze with appropriate tags.
            instance.populate_from_mp4_tags(file_path, file_name)
        else:
            # New Song, scan ID3 tags for file.
            instance.populate_from_id3_tags(file_path, file_name)


signals.pre_save.connect(song_pre_save, sender=Song)


def song_pre_delete(sender, instance, *args, **kwargs):
    """
    Clean up misc. stuff before a Song is deleted.
    """
    if instance.file is not None:
        instance.file.delete()


signals.pre_delete.connect(song_pre_delete, sender=Song)

SONG_RATINGS = (
    (1, '1 - Lousy'),
    (2, '2 - Meh'),
    (3, '3 - Good'),
    (4, '4 - Epic'),
)


class SongRating(models.Model):
    """
    Represents a rating for a song, as provided by an authenticated User.
    """
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True, choices=SONG_RATINGS)

    class Meta:
        unique_together = ("song", "user")


def songrating_post_save(sender, instance, created, *args, **kwargs):
    """
    Recaculate the Song's average rating.
    """
    song = instance.song
    song_ratings = song.songrating_set.filter(rating__isnull=False)
    song_num_ratings = song_ratings.count()
    aggregates = song_ratings.aggregate(models.Avg('rating'))
    song.rating = aggregates['rating__avg']
    song.num_ratings = song_num_ratings
    song.save()


signals.post_save.connect(songrating_post_save, sender=SongRating)
