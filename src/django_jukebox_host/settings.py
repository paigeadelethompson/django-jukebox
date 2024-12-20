import os, sys
from pathlib import Path
from .wrapping_paper import conf

BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_PATH = BASE_DIR
DOT_DIR = conf.get_dot_directory()
MEDIA_ROOT = conf.create_dir_if_not_exists(DOT_DIR / "media")
MUSIC_DIR_NAME = "music"
MUSIC_DIR = conf.create_dir_if_not_exists(DOT_DIR / MUSIC_DIR_NAME)
STATIC_ROOT = conf.create_dir_if_not_exists(DOT_DIR / "static")

STATIC_URL = 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
MEDIA_URL = 'media/'
YUI_URL = 'http://yui.yahooapis.com/2.8.0r4/'
LOGIN_REDIRECT_URL = '/'


PROGRAM_NAME = conf.get_name()
RANDOM_REQ_GOOD_RATED_SONGS = 10
RANDOM_REQ_GOOD_RATING = 3
RANDOM_REQ_UPCOMING = 6
RANDOM_REQ_UPCOMING_MAX_RATINGS = 4
TIME_TO_SLEEP_WHEN_QUEUE_EMPTY = 10
NUMBER_OF_PREVIOUS_SONGS_DISPLAY = 5
LIMIT_UPCOMING_SONGS_DISPLAY = 15
MAX_OUTSTANDING_REQUESTS_PER_USER = 5
MAX_SONG_LENGTH = 15. * 60.
MIN_SONG_LENGTH = 60.
ALLOW_ANON_REQUESTS = False
CLI_PLAYER_COMMAND_STR = ['mplayer', '-really-quiet', '-af', 'volume']
DJANGO_SERVE_MEDIA = True
ADMINS = (('Your Name', 'your_email@domain.com'))
MANAGERS = ADMINS
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
SECRET_KEY = None
ROOT_URLCONF = 'django_jukebox_host.urls'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEBUG = True
TEMPLATE_DEBUG = True
CSRF_USE_SESSIONS = True

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]']



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DOT_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django_jukebox_host',
    'django_jukebox.accounts',
    'django_jukebox.juke_daemon',
    'django_jukebox.juketunes_ui',
    'django_jukebox.music_db',
    'django_jukebox.music_player',
    'django.contrib.admindocs',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_extensions',
    'django_otp',
    'django_otp.plugins.otp_totp',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django_jukebox.includes.extra_context.common_urls',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

sys.path.insert(0, str(conf.get_dot_directory()))
from settings import *
sys.path.pop(0)