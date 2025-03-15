"""
Настройки Django для проекта base.

Сгенерировано с помощью 'django-admin startproject' (Django 5.1.7).

Документация по файлу настроек:
https://docs.djangoproject.com/en/5.1/topics/settings/

Полный список настроек:
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Определяем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# ВАЖНО! Эти настройки предназначены для разработки. Для продакшена нужно внести изменения!
# См. чек-лист развертывания: https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Секретный ключ приложения Django
SECRET_KEY = 'django-insecure-tn1cecbc5p3ytgezd-n(r07zg!sd)u(z2-wvei)o_&4sayke)j'

# Режим отладки (Debug)
DEBUG = True

# Разрешенные хосты
ALLOWED_HOSTS = [
    'django.lan',
    '192.168.1.174',
    '127.0.0.1',
    'localhost',
    'fat-duck.lan'
]

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Для REST API
    'accounts',
    'bookings',
    'orders',
]

# Промежуточное ПО (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Основной файл маршрутизации
ROOT_URLCONF = 'base.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'base/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

# Настройки WSGI
WSGI_APPLICATION = 'base.wsgi.application'

# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Настройки проверки паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Настройки статических файлов
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Настройки медиафайлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Тип поля для автоинкрементного первичного ключа
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Перенаправления после входа и выхода
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/'

# Автоматически добавлять слэш в конце URL
APPEND_SLASH = True