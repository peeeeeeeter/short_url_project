from django.views.generic import RedirectView, TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound

from .models import ShortUrl
from .utils import b62_decode

class IndexView(TemplateView):
    http_method_names = ['get']
    template_name = 'shorten_urls/index.html'


class ShortUrlRedirectView(RedirectView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        short_url = kwargs.get('short_url')
        not_found_message = '<h1>404 Not Found</h1>'

        if not 1 <= len(short_url) <= 5:
            return HttpResponseNotFound(not_found_message)

        try:
            url_id = b62_decode(short_url)
        except (KeyError, ValueError):
            return HttpResponseNotFound(not_found_message)

        try:
            short_url_object = ShortUrl.objects.get(id=url_id)
        except ShortUrl.DoesNotExist:
            return HttpResponseNotFound(not_found_message)

        return HttpResponseRedirect(short_url_object.original_url)