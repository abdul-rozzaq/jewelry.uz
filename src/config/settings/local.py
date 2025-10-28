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
