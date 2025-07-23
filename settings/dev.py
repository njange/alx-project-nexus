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

AUTH_USER_MODEL = 'users.CustomUser'