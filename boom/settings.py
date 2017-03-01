import environ
import os

# inner project dir
base_dir = environ.Path(__file__) - 1
BASE_DIR = base_dir()

# outside project dir
root_dir = base_dir - 1

# load the default env file
env = environ.Env(DEBUG=(bool, False),)
environ.Env.read_env(root_dir.path('.env')())

# core env variables
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
INTERNAL_IPS = env.list('INTERNAL_IPS', default=[])
HTTPS_ONLY = env.bool('HTTPS_ONLY', default=False)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'storages',
    'api',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root_dir('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'boom.wsgi.application'

DATABASES = {
    'default': env.db(
        default='sqlite:///{}'.format(base_dir('db.sqlite3'))
    )
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

LANGUAGE_CODE = env.str('LANGUAGE_CODE', default='en-us')
TIME_ZONE = env.str('TIME_ZONE', default='UTC')
USE_I18N = env.bool('USE_I18N', default=True)
USE_L10N = env.bool('USE_L10N', default=True)
USE_TZ = env.bool('USE_TZ', default=True)

# If overriding ensure trailing slash is present, e.g. 'boom/'
APP_CONTEXT = env.str('APP_CONTEXT', default='')

CRISPY_TEMPLATE_PACK = env.str('CRISPY_TEMPLATE_PACK', default='bootstrap3')
STATICFILES_DIRS = (
    os.path.join(
        base_dir('static')
    ),
)

# allow zappa settings to switch media storage to s3
DEFAULT_FILE_STORAGE = env.str(
    'DEFAULT_FILE_STORAGE',
    default='django.core.files.storage.FileSystemStorage')

# zappa will switch static storage to s3
STATICFILES_STORAGE = env.str(
    'STATICFILES_STORAGE',
    default='django.contrib.staticfiles.storage.StaticFilesStorage')

# sets the bucket to upload static files into
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', default='')
AWS_AUTO_CREATE_BUCKET = True

# if a bucket name is provided, set the s3 url for static files
if len(AWS_STORAGE_BUCKET_NAME):
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    DEFAULT_STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
else:
    DEFAULT_STATIC_URL = APP_CONTEXT + '/static/'

# use a default static url, but still allow overriding through the env
STATIC_URL = env.str('STATIC_URL', default=DEFAULT_STATIC_URL)
