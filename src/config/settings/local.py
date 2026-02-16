# ruff: noqa: F403, F405

from .base import *


DEBUG = True


# Enable Django Silk in local environment
INSTALLED_APPS += [
    "silk",
]

# Place SilkyMiddleware near the top so it can profile as much as possible
MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
] + MIDDLEWARE


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR.parent / "cache_files",
    },
    "redis": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    },
}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DB_NAME", default="jewelry_db"),
        "USER": env.str("DB_USER", default="postgres"),
        "PASSWORD": env.str("DB_PASSWORD", default="password"),
        "HOST": env.str("DB_HOST", default="127.0.0.1"),
        "PORT": env.str("DB_PORT", default="5432"),
    }
}
