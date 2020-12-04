from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.views.generic import RedirectView, TemplateView

from .configs import REDIRECT_URL_REDIS_PREFIX
from .logics import decode_short_url
from .models import ShortUrl


class IndexView(TemplateView):
    http_method_names = ['get']
    template_name = 'shorten_urls/index.html'


class ShortUrlRedirectView(RedirectView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        short_url = kwargs.get('short_url')
        not_found_message = '<h1>404 Not Found</h1>'

        cache_key = REDIRECT_URL_REDIS_PREFIX + short_url

        if settings.ENABLE_CACHE:
            cached_url = cache.get(cache_key)
            if  cached_url:
                return HttpResponseRedirect(cached_url)

        try:
            url_id = decode_short_url(short_url)
        except (KeyError, ValueError):
            return HttpResponseNotFound(not_found_message)

        try:
            short_url_object = ShortUrl.objects.get(id=url_id)
        except ShortUrl.DoesNotExist:
            return HttpResponseNotFound(not_found_message)

        original_url = short_url_object.original_url

        if settings.ENABLE_CACHE:
            cache.set(cache_key, original_url)

        return HttpResponseRedirect(original_url)
