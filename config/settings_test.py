from .settings import *
import os

# =========== НАСТРОЙКИ ДЛЯ ТЕСТОВ ===========

# Переопределяем базу данных - используем SQLite в памяти
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'test-key-12345-for-tests-only'

DEBUG = True

ALLOWED_HOSTS = ['*']

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Настройки для статических файлов
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
