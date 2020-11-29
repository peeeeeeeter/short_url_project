from .configs import CRAWL_URL_PREVIEW_TIMEOUT
from .models import ShortUrl
from .utils import UrlPreivew, b62_encode

from django.conf import settings


class ShortUrlLogics:

    def __init__(self, url, *args, **kwargs):
        self.url = url

    def get_or_create_short_url(self):
        short_url_object, _ = ShortUrl.objects.get_or_create(
            original_url=self.url
        )

        number = short_url_object.id
        return {
            'short_url_path': b62_encode(number),
            'original_url': self.url,
        }

    def get_short_url_preview_data(self):
        preview = UrlPreivew(self.url, timeout=CRAWL_URL_PREVIEW_TIMEOUT)
        preview.fire()

        preview_data = {}
        if preview.success:
            preview_data = preview.as_dict()

        return preview_data

    def get_shor_url_data(self):
        data = {}

        short_url_data = self.get_or_create_short_url()
        data['short_url_path'] = short_url_data['short_url_path']
        data['original_url'] = short_url_data['original_url']

        preview_data = self.get_short_url_preview_data()
        data['preview_data'] = preview_data

        return data