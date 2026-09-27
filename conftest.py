import django
from django.conf import settings


def pytest_configure():
    settings.DATABASES['default'].update({
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    })
    settings.STORAGES['staticfiles']['BACKEND'] = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    django.setup()
