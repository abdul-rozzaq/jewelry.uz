from functools import wraps
from django.core.cache import cache

from rest_framework.response import Response


def cache_response(timeout=300, key_func=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            # Custom cache key yaratish

            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = f"api_{request.path}_{request.user.id}_{request.GET.urlencode()}"

            # Cache dan ma'lumot olish
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)

            # Agar cache da yo'q bo'lsa, asl funksiyani chaqirish
            response = view_func(self, request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)

            return response

        return _wrapped_view

    return decorator
