import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'nexus_db'),
        'USER': os.getenv( 'POSTGRES_USER', 'nexus_user'),
        'PASSWORD': os.getenv( 'POSTGRES_PASSWORD', 'nexus_password'),
        'HOST': os.getenv( 'POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv( 'POSTGRES_PORT', '5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{os.getenv("REDIS_HOST", "localhost")}:{os.getenv("REDIS_PORT", "6379")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.getenv('REDIS_PASSWORD', None),
        }
    }
}   