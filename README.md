# Shelved 
until further notice 

# django-jukebox #

Web-based jukebox system written in Django.

This was a fork containing some patches versus the original project at [Google Code](https://code.google.com/p/django-jukebox/).


# Installation

- `poetry install`
- `poetry build`
- `pip install --user dist/*.whl`

# Configuration
- `export PATH=$HOME/.local/bin:$PATH`
- `django_jukebox_admin migrate`
- `django_jukebox_admin createsuperuser`
- `django_jukebox_admin collectstatic`

## Data location 
- `django_jukebox_admin` automatically creates a `.django-jukebox` directory in your home directory: 

```
.django-jukebox
├── __pycache__
│   └── settings.cpython-311.pyc
├── db.sqlite3
├── media
├── music
├── settings.py
└── static
...
```

The settings.py file contains the secret key for seession encryption and any other overrides can be specified here as well.

# Start the server
- `django-jukebox_admin runserver`
