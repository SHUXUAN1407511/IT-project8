from pathlib import Path

from config.environment import BASE_DIR, env


SECRET_KEY = env.secret_key

DEBUG = env.debug

ALLOWED_HOSTS = env.allowed_hosts



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Assignment.apps.AssignmentConfig',
    'corsheaders',
    'rest_framework',
    'usersystem',
    'AIUseScale.apps.AiusescaleConfig',
    'courses',
    'template',
    'exports',
    'notifications',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'itp8.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins':['django.templatetags.static']
        },
    },
]

WSGI_APPLICATION = 'itp8.wsgi.application'



DATABASES = {
    'default': env.database
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'POST',
    'PATCH',
    'PUT',
    'OPTIONS',
    'VIEW',
    'GET'
)

CORS_ALLOW_HEADERS = (
    '*'
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'usersystem.authentication.BearerTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    )
}



STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = env.email_backend
EMAIL_HOST = env.email_host
EMAIL_PORT = env.email_port
EMAIL_HOST_USER = env.email_host_user
EMAIL_HOST_PASSWORD = env.email_host_password
EMAIL_USE_TLS = env.email_use_tls
EMAIL_USE_SSL = env.email_use_ssl
DEFAULT_FROM_EMAIL = env.default_from_email

PASSWORD_RESET_TOKEN_EXPIRY_MINUTES = env.password_reset_token_expiry_minutes
PASSWORD_RESET_URL = env.password_reset_url

CORS_ALLOWED_ORIGINS = env.cors_allowed_origins
CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins
